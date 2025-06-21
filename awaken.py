with open("click.flag", "w") as f:
    f.write("clicked")

with open("click.log", "a") as log:
    from datetime import datetime
    log.write(f"Clicked at {datetime.now()}\n")