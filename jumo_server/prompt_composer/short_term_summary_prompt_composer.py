from jumo_server.memory.episodic.db.short_term_collection import ShortTermMemorySummary, short_term_episodic_memory_collection
from jumo_server.prompt_composer.prompt_composer import PromptComposer


class ShortTermSummaryPromptComposer(PromptComposer):
    summaries: list[ShortTermMemorySummary] = []

    async def prep(self):
        self.summaries = await short_term_episodic_memory_collection.find({}).sort([("created_at", -1)]).limit(10).to_list()

    def compose(self) -> str:
        output = "<short_term_memory>\n"

        for composer in self.summaries:
            output += f"<summary created_at='{composer['created_at']}'>\n{composer['summary']}\n</summary>\n"
            output += "\n\n"

        output += "</short_term_memory>"

        return output
