import logging

import requests
from bs4 import BeautifulSoup

from course_llm_engineering.utils import query_trough_openai

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(asctime)s:%(funcName)s: %(message)s",
    datefmt="%H:%M:%S",
)


class Website:
    # Some websites need you to use proper headers when fetching them
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    }

    def __init__(self, url):
        """
        A utility class to represent a Website that we have scraped to obtain the links
        """

        self.logger = logging.getLogger("Website")
        self.logger.info("Extracting content from main url ...")
        self.url = url
        response = requests.get(url, headers=self.HEADERS)
        self.body = response.content
        soup = BeautifulSoup(self.body, "html.parser")
        self.title = soup.title.string if soup.title else "No title found"
        self.text, self.links = self.get_website_elements(soup)

    @staticmethod
    def get_website_elements(soup):
        if soup.body:
            for irrelevant in soup.body(["script", "style", "img", "input"]):
                irrelevant.decompose()
            text = soup.body.get_text(separator="\n", strip=True)
        else:
            text = ""
        links = [link.get("href") for link in soup.find_all("a")]
        links = [link for link in links if link]
        return text, links

    def get_contents(self):
        return f"Webpage Title:\n{self.title}\nWebpage Contents:\n{self.text}\n\n"


class WebsiteLinkFilter:
    SYSTEM_PROMPT = (
        "You are provided with a list of links found on a webpage. "
        "You are able to decide which of the links would be most relevant to include in a brochure about the company, "
        "such as links to an About page, or a Company page, or Careers/Jobs pages.\n"
        "You should respond in JSON as in this example:"
        """
        {
            "links": [
                {"type": "about page", "url": "https://full.url/goes/here/about"},
                {"type": "careers page": "url": "https://another.full.url/careers"}
            ]
        }
        """
    )
    USER_PROMPT = user_prompt = (
        "Here is the list of links on the website of {website_url} - "
        "please decide which of these are relevant web links for a brochure about the company, "
        "respond with the full https URL in JSON format. "
        "Example of relative to full url conversion: /about -> {website_url}/about. "
        "Do not include Terms of Service, Privacy, email links.\n"
        "Links (some might be relative links):\n"
    )

    def __init__(self, llm_model: str, use_ollama: bool = True):
        self.logger = logging.getLogger("WebsiteLinkFilter")

        self.llm_model = llm_model
        self.use_ollama = use_ollama
        self.filtered_links = None

    def build_user_prompt(self, website: Website):
        user_prompt = self.USER_PROMPT.format(website_url=website.url)
        user_prompt += "\n".join(website.links)
        return user_prompt

    def filter_links(self, website: Website):
        self.logger.info(
            "Filtering relevant urls within main website to complement information ..."
        )
        user_prompt = self.build_user_prompt(website)
        print(user_prompt)
        self.filtered_links = query_trough_openai(
            user_prompt=user_prompt,
            system_prompt=self.SYSTEM_PROMPT,
            model=self.llm_model,
            ollama=True,
            optional_arguments={"response_format": {"type": "json_object"}},
        )
        return self.filtered_links


class CompanyBrochureGenerator:
    SYSTEM_PROMPT = (
        "You are an assistant that analyzes the contents of several relevant pages from a company website "
        "and creates a short brochure about the company for prospective customers, investors, and recruits. "
        "Respond in html. Include details of company culture, customers, and careers/jobs if you have the information."
    )

    USER_PROMPT = (
        "You are looking at a company called: {company_name}\n"
        "Here are the contents of its landing page and other relevant pages; "
        "use this information to build a short brochure of the company in html.\n"
    )

    def __init__(self, company_name: str, url: str, llm_model: str, use_ollama: bool):
        self.logger = logging.getLogger("CompanyBrochureGenerator")
        self.company_name = company_name
        self.website_url = url
        self.llm_model = llm_model
        self.use_ollama = use_ollama
        self.website = Website(url)
        self.website_filter = WebsiteLinkFilter(llm_model)
        self.relevant_links = None
        self.brochure = None

    def extract_relevant_content_from_website(self):
        """Fetches the content of relevant pages from the main url, filtering links."""
        result = "Landing page:\n"
        result += self.website.get_contents()

        # Extract relevant links using WebsiteLinkFilter
        self.relevant_links = self.website_filter.filter_links(self.website)

        if not self.relevant_links or "links" not in self.relevant_links:
            return result

        self.logger.info(
            f"Extracting additional information from {len(self.relevant_links)} links."
        )

        for link in self.relevant_links["links"]:
            self.logger.info(f"Extracting additional information from f{link}")
            result += f"\n\n{link['type']}\n"
            result += Website(link["url"]).get_contents()

        return result

    def build_user_prompt(self):
        """Builds a user prompt for generating the company brochure."""
        user_prompt = (
            self.USER_PROMPT.format(company_name=self.company_name)
            + self.extract_relevant_content_from_website()
        )
        return user_prompt[:5_000]  # Truncate if more than 5,000 characters

    def create_brochure(self):
        """Generates the company brochure using a LLM model."""

        self.logger.info("Generating brochure...")
        self.brochure = query_trough_openai(
            user_prompt=self.build_user_prompt(),
            system_prompt=self.SYSTEM_PROMPT,
            model=self.llm_model,
            optional_arguments={"response_format": {"type": "json_object"}},
        )
        self.logger.info("Saving brochure to brochure.html...")
        with open("brochure.html", "w", encoding="utf-8") as f:
            f.write(self.brochure)


if __name__ == "__main__":
    brochureGenerator = CompanyBrochureGenerator(
        "HuggingFace", "https://huggingface.co", llm_model="gemma3:4b", use_ollama=True
    )

    brochureGenerator.create_brochure()
    print("Brochure completed!")
