import openai
import requests
from bs4 import BeautifulSoup


class Website:
    # Some websites need you to use proper headers when fetching them
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    }

    def __init__(self, url):
        """
        Create this Website object from the given url using the BeautifulSoup library
        """
        self.url = url
        response = requests.get(url, headers=self.HEADERS)
        soup = BeautifulSoup(response.content, "html.parser")
        self.title = soup.title.string if soup.title else "No title found"
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()
        self.text = soup.body.get_text(separator="\n", strip=True)


class Summarizer:
    SYSTEM_PROMPT = (
        "You are an assistant that analyzes the contents of a website "
        "and provides a short summary, ignoring text and symbols that might be navigation related or cannot be read. "
        "Respond in markdown."
    )

    def __init__(self, url: str, model: str) -> None:
        self.model = model
        self.url = url

        self.website = None
        self.user_prompt = None
        self.request = None
        self.response = None

    def user_prompt_for_website(self):
        user_prompt = (
            f"You are looking at a website titled {self.website.title} "
            "\nThe contents of this website is as follows; "
            "please provide a short summary of this website in markdown. "
            "Be concise, only provided the requested content without asking for next tasks.\n\n"
        )
        user_prompt += self.website.text
        return user_prompt

    def request_for_summarizer(self):
        return [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": self.user_prompt},
        ]

    def query_model(self):
        ollama_via_openai = openai.OpenAI(
            base_url="http://localhost:11434/v1", api_key="ollama"
        )

        return ollama_via_openai.chat.completions.create(
            model=self.model, messages=self.request
        )

    def display_and_save_summary(self):
        summary = self.response.choices[0].message.content
        print(summary)
        with open("summary.md", "w", encoding="utf-8") as f:
            f.write(summary)

    def summarize(self):
        self.website = Website(self.url)
        self.user_prompt = self.user_prompt_for_website()
        self.request = self.request_for_summarizer()
        self.response = self.query_model()
        self.display_and_save_summary()


if __name__ == "__main__":
    summarizer = Summarizer(url="https://edwarddonner.com", model="gemma3:4b")
    summarizer.summarize()
