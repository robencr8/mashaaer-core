
```python
from robin_inspector import generate_app_report

def ask_replit_for_app_report():
    report = generate_app_report(
        include_dependencies=True,
        include_missing_env=True,
        include_routes=True,
        include_startup_check=True,
        include_disk_structure=True,
        include_ports=True,
        include_logs=True
    )
    
    print("📊 Robin AI App Report:\n")
    print(report)
    return report

if __name__ == "__main__":
    ask_replit_for_app_report()
```
