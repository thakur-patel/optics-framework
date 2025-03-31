# execution.py
import asyncio
from abc import ABC, abstractmethod
from typing import Optional, Dict
from optics_framework.common.session_manager import SessionManager, Session
from optics_framework.common.runner.test_runnner import TestRunner, TreeResultPrinter, TerminalWidthProvider, IResultPrinter, TestCaseResult
from optics_framework.common.runner.keyword_register import KeywordRegistry
from optics_framework.api import ActionKeyword, AppManagement, FlowControl, Verifier


class NullResultPrinter(IResultPrinter):
    """A no-op implementation of IResultPrinter for cases where no output is needed."""

    def __init__(self):
        self._test_state: Dict[str, TestCaseResult] = {}

    @property
    def test_state(self) -> Dict[str, TestCaseResult]:
        return self._test_state

    @test_state.setter
    def test_state(self, value: Dict[str, TestCaseResult]) -> None:
        self._test_state = value

    def print_tree_log(self, test_case_result: TestCaseResult) -> None:
        pass

    def start_live(self) -> None:
        pass

    def stop_live(self) -> None:
        pass

    def start_run(self, total_test_cases: int) -> None:
        pass


class Executor(ABC):
    """Abstract base class for execution strategies."""
    @abstractmethod
    async def execute(self, session: Session, runner: TestRunner, event_queue: Optional[asyncio.Queue]) -> None:
        pass


class BatchExecutor(Executor):
    """Executes a batch test case from preloaded CSV data."""

    def __init__(self, test_case: Optional[str] = None):
        self.test_case = test_case

    async def execute(self, session: Session, runner: TestRunner, event_queue: Optional[asyncio.Queue]) -> None:
        if not runner.test_cases:
            status = "ERROR"
            message = "No test cases loaded"
            if event_queue:
                await event_queue.put({"execution_id": session.session_id, "status": status, "message": message})
            raise ValueError(message)

        if self.test_case:
            if self.test_case not in runner.test_cases:
                status = "ERROR"
                message = f"Test case {self.test_case} not found in loaded data"
                if event_queue:
                    await event_queue.put({"execution_id": session.session_id, "status": status, "message": message})
                raise ValueError(message)
            result = runner.execute_test_case(self.test_case)
            status = "PASS" if result["status"] == "PASS" else "FAIL"
            message = f"Test case {self.test_case} completed with status {status}"
        else:
            runner.run_all()
            status = "PASS" if all(
                tc["status"] == "PASS" for tc in runner.result_printer.test_state.values()) else "FAIL"
            message = "All test cases completed"

        if event_queue:
            await event_queue.put({"execution_id": session.session_id, "status": status, "message": message})


class DryRunExecutor(Executor):
    """Performs a dry run of a test case from preloaded CSV data."""

    def __init__(self, test_case: Optional[str] = None):
        self.test_case = test_case

    async def execute(self, session: Session, runner: TestRunner, event_queue: Optional[asyncio.Queue]) -> None:
        if not runner.test_cases:
            status = "ERROR"
            message = "No test cases loaded"
            if event_queue:
                await event_queue.put({"execution_id": session.session_id, "status": status, "message": message})
            raise ValueError(message)

        if self.test_case:
            if self.test_case not in runner.test_cases:
                status = "ERROR"
                message = f"Test case {self.test_case} not found in loaded data"
                if event_queue:
                    await event_queue.put({"execution_id": session.session_id, "status": status, "message": message})
                raise ValueError(message)
            result = runner.dry_run_test_case(self.test_case)
            status = "PASS" if result["status"] == "PASS" else "FAIL"
            message = f"Dry run for test case {self.test_case} completed with status {status}"
        else:
            runner.dry_run_all()
            status = "PASS" if all(
                tc["status"] == "PASS" for tc in runner.result_printer.test_state.values()) else "FAIL"
            message = "All test cases dry run completed"

        if event_queue:
            await event_queue.put({"execution_id": session.session_id, "status": status, "message": message})


class KeywordExecutor(Executor):
    """Executes a single keyword."""

    def __init__(self, keyword: str, params: list[str]):
        self.keyword = keyword
        self.params = params

    async def execute(self, session: Session, runner: TestRunner, event_queue: Optional[asyncio.Queue]) -> None:
        method = runner.keyword_map.get("_".join(self.keyword.split()).lower())
        if method:
            method(*self.params)
            if event_queue:
                await event_queue.put({
                    "execution_id": session.session_id,
                    "status": "PASS",
                    "keyword": self.keyword,
                    "message": "Keyword executed successfully"
                })
        else:
            if event_queue:
                await event_queue.put({
                    "execution_id": session.session_id,
                    "status": "FAIL",
                    "keyword": self.keyword,
                    "message": "Keyword not found"
                })
            raise ValueError(f"Keyword {self.keyword} not found")


class RunnerFactory:
    """Sets up a TestRunner with keywords and preloaded data."""
    @staticmethod
    def create_runner(
        session: Session,
        use_printer: bool,
        test_cases: Dict,
        modules: Dict,
        elements: Dict
    ) -> TestRunner:
        result_printer = TreeResultPrinter(
            TerminalWidthProvider()) if use_printer else NullResultPrinter()
        runner = TestRunner(
            test_cases=test_cases,
            modules=modules,
            elements=elements,
            keyword_map={},
            result_printer=result_printer
        )
        registry = KeywordRegistry()
        flow_control = FlowControl(runner)
        action_keyword = session.optics.build(ActionKeyword)
        app_management = session.optics.build(AppManagement)
        verifier = session.optics.build(Verifier)
        registry.register(action_keyword)
        registry.register(app_management)
        registry.register(flow_control)
        registry.register(verifier)
        runner.keyword_map = registry.keyword_map
        return runner


class ExecutionEngine:
    """Orchestrates execution using session management and executor strategies."""

    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager

    async def execute(
        self,
        session_id: str,
        mode: str,
        test_case: Optional[str] = None,
        keyword: Optional[str] = None,
        params: list[str] = [],
        event_queue: Optional[asyncio.Queue] = None,
        test_cases: Optional[Dict] = None,
        modules: Optional[Dict] = None,
        elements: Optional[Dict] = None
    ) -> None:
        session = self.session_manager.get_session(session_id)
        if not session:
            if event_queue:
                await event_queue.put({"status": "ERROR", "message": "Session not found"})
            raise ValueError("Session not found")

        runner = RunnerFactory.create_runner(
            session,
            use_printer=event_queue is None,
            test_cases=test_cases or {},
            modules=modules or {},
            elements=elements or {}
        )
        if runner.result_printer:
            runner.result_printer.start_live()

        if mode == "batch":
            executor = BatchExecutor(test_case)
        elif mode == "dry_run":
            executor = DryRunExecutor(test_case)
        elif mode == "keyword":
            if not keyword:
                if event_queue:
                    await event_queue.put({"status": "ERROR", "message": "Keyword mode requires a keyword"})
                raise ValueError("Keyword mode requires a keyword")
            executor = KeywordExecutor(keyword, params)
        else:
            if event_queue:
                await event_queue.put({"status": "ERROR", "message": f"Unknown mode: {mode}"})
            raise ValueError(f"Unknown mode: {mode}")

        try:
            if event_queue:
                await event_queue.put({
                    "execution_id": session_id,
                    "status": "RUNNING",
                    "message": f"Starting {mode} execution"
                })
            await executor.execute(session, runner, event_queue)
        except Exception as e:
            if event_queue:
                await event_queue.put({"status": "FAIL", "message": f"Execution failed: {str(e)}"})
            raise
        finally:
            if runner.result_printer:
                runner.result_printer.stop_live()
