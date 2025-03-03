import subprocess
import sys
import requests
import openai
from bs4 import BeautifulSoup
import random
import time
import os
from dotenv import load_dotenv  # Import dotenv

# Ensure dependencies are installed
def install_packages():
    required_packages = ["openai", "requests", "beautifulsoup4", "pydantic", "python-dotenv"]
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"Installing missing package: {package}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_packages()

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    raise ValueError("⚠️ OpenAI API key not found. Make sure it's set in the .env file.")

openai.api_key = openai_api_key

print("✅ API Key Loaded Successfully (but not printed for security reasons)")

# Startup evaluation factors
class StartupEvaluator:
    def __init__(self, company_name):
        self.company_name = company_name
        self.data = {
            "Market Opportunity": None,
            "Problem & Solution Fit": None,
            "Competitive Advantage": None,
            "Team Strength": None,
            "Exit Potential": None,
            "Revenue Growth": None,
            "Burn Rate & Runway": None,
            "Funding History": None,
            "Customer Adoption": None,
            "Valuation & Cap Table": None
        }

    def fetch_company_info(self):
        """Try to fetch startup data using Google search."""
        print(f"🔍 Fetching data for {self.company_name}...")

        search_url = f"https://www.google.com/search?q={self.company_name.replace(' ', '+')}+startup+funding"
        try:
            response = requests.get(search_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                snippets = [snip.text for snip in soup.find_all("span")][:3]
                print("✅ Fetched some info:", snippets)
                return snippets
        except requests.exceptions.Timeout:
            print("⚠️ Google search timed out. Skipping...")
        except Exception as e:
            print(f"⚠️ Could not fetch data automatically: {e}")
        return None

    def ask_openai(self, prompt):
        """Uses OpenAI to generate insights on the startup."""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                timeout=15  # Prevents long waiting times
            )
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            print("⚠️ Error fetching data from OpenAI:", e)
            return None

    def analyze_startup(self):
        """Use OpenAI to evaluate all qualitative metrics in a single call."""
        print("🤖 Calling OpenAI API for analysis...")

        multi_question_prompt = f"""
        Please analyze the startup "{self.company_name}" based on these criteria:
        
        1. Market Opportunity: Describe market size, growth rate, and industry trends.
        2. Problem & Solution Fit: Explain what problem this startup solves and how it compares to existing solutions.
        3. Competitive Advantage: What makes this company unique? Does it have a defensible moat?
        4. Team Strength: Who are the founders and their expertise? Is this a strong team?
        5. Exit Potential: What are the potential exit strategies (acquisition, IPO, etc.)?
        6. Revenue Growth: Analyze the company's revenue trends.
        7. Burn Rate & Runway: Assess how long the company can sustain operations.
        8. Funding History: Summarize funding rounds, investors, and total capital raised.
        9. Customer Adoption: Evaluate user growth and traction.
        10. Valuation & Cap Table: Estimate valuation and ownership structure.

        Please provide structured answers in the following format:

        Market Opportunity: <answer>
        Problem & Solution Fit: <answer>
        Competitive Advantage: <answer>
        Team Strength: <answer>
        Exit Potential: <answer>
        Revenue Growth: <answer>
        Burn Rate & Runway: <answer>
        Funding History: <answer>
        Customer Adoption: <answer>
        Valuation & Cap Table: <answer>
        """

        response = self.ask_openai(multi_question_prompt)

        if response:
            # Ensure response is structured
            for key in self.data.keys():
                if f"{key}:" in response:
                    self.data[key] = response.split(f"{key}:")[1].split("\n")[0].strip()

        # Debugging: Check if OpenAI successfully populated the fields
        print("🔍 AI-Generated Data:", self.data)

    def evaluate(self):
        """Assign scores based on AI-generated data quality."""
        scores = {}
        for key, value in self.data.items():
            if value:
                scores[key] = min(10, max(1, len(value) % 10))  # Basic heuristic
            else:
                scores[key] = random.randint(1, 5)  # Assign low score if missing

        total_score = sum(scores.values()) / len(scores)
        return total_score, scores

    def generate_report(self, score, detailed_scores):
        """Generate a final report with investment recommendation."""
        print("\n📊 --- Investment Evaluation Report --- 📊")
        print(f"**Company:** {self.company_name}")
        print(f"**Investment Score:** {score:.1f}/10")

        for key, value in detailed_scores.items():
            print(f"- {key}: {value}/10")

        # Final Recommendation
        if score >= 8:
            print("\n✅ **Recommendation:** Strong investment candidate 🚀")
        elif score >= 5:
            print("\n📊 **Recommendation:** Promising, but needs further due diligence.")
        else:
            print("\n⚠️ **Recommendation:** High risk. Not recommended at this stage.")

    def run(self):
        """Run the full evaluation process with improved performance."""
        print("🔍 Fetching company information...")
        fetched_info = self.fetch_company_info()

        if fetched_info:
            print("✅ Found some data. Now using AI for deeper analysis...")

        print("🤖 Calling OpenAI API for insights...")
        self.analyze_startup()

        print("📊 Evaluating startup...")
        final_score, detailed_scores = self.evaluate()

        print("📄 Generating final report...")
        self.generate_report(final_score, detailed_scores)

        print("✅ Done!")

# Run the tool for a startup
if __name__ == "__main__":
    company_name = input("Enter the startup name: ")
    evaluator = StartupEvaluator(company_name)
    evaluator.run()
