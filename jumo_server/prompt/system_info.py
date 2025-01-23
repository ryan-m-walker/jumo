from datetime import datetime


def get_system_info() -> str:
    return (
        "## System Info:\n\n"
        f"Todays date is {datetime.now()}\n"
        f"Timezone is {datetime.now().astimezone().tzinfo}\n"
    )
