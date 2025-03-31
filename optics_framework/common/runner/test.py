from time import sleep
from rich.live import Live
from rich.table import Table

def generate_table():
    table = Table(title="Live Data Table")
    table.add_column("Row", justify="right", style="cyan", no_wrap=True)
    table.add_column("Description", style="magenta")
    table.add_column("Value", justify="right", style="green")
    
    for row in range(1, 11):
        table.add_row(str(row), f"Description {row}", f"{row * 10}")
    return table

with Live(generate_table(), refresh_per_second=2) as live:
    for _ in range(20):  # Update the table 20 times
        sleep(0.5)
        live.update(generate_table())