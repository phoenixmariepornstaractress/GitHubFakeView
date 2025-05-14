import requests
import time
import random
import logging
import json
import base64
import os
from datetime import datetime
from urllib.parse import urlparse

class GitHubViewBooster:
    def __init__(self, url: str, view_count: int):
        self.url = url
        self.view_count = view_count
        self.successful_views = 0
        self.failed_views = 0
        self.logs = []
        self.session_start = datetime.now()
        logging.basicConfig(
            filename="view_booster.log",
            level=logging.INFO,
            format="%(asctime)s - %(message)s"
        )

    def send_fake_views(self, delay_range=(1, 2)):
        for i in range(self.view_count):
            try:
                headers = self._random_headers()
                response = requests.get(self.url, headers=headers)
                if response.status_code == 200:
                    self.successful_views += 1
                    msg = f"Fake view {i + 1} successful."
                else:
                    self.failed_views += 1
                    msg = f"View {i + 1} failed. Status code: {response.status_code}"
            except requests.RequestException as e:
                self.failed_views += 1
                msg = f"View {i + 1} failed due to error: {e}"

            self.logs.append(msg)
            logging.info(msg)
            time.sleep(random.uniform(*delay_range))

    def _random_headers(self):
        agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "Mozilla/5.0 (X11; Linux x86_64)"
        ]
        return {"User-Agent": random.choice(agents)}

    def summary_report(self):
        return {
            "session_start": self.session_start.strftime("%Y-%m-%d %H:%M:%S"),
            "url": self.url,
            "total": self.view_count,
            "successful": self.successful_views,
            "failed": self.failed_views
        }

    def validate_url(self):
        try:
            return requests.head(self.url).status_code == 200
        except:
            return False

    def save_report(self, filename=".boost_report.txt"):
        report_data = {
            "summary": self.summary_report(),
            "logs": self.logs
        }
        encoded = base64.b64encode(json.dumps(report_data).encode()).decode()
        with open(filename, 'w') as f:
            f.write(encoded)

    def hide_report_file(self, filename=".boost_report.txt"):
        try:
            if os.name == 'nt':
                os.system(f"attrib +h {filename}")
            else:
                hidden_name = "." + filename if not filename.startswith(".") else filename
                os.rename(filename, hidden_name)
        except Exception as e:
            self.logs.append(f"Error hiding file: {e}")

    def reset(self):
        self.successful_views = 0
        self.failed_views = 0
        self.logs.clear()

    def set_target(self, url: str, view_count: int = None):
        self.url = url
        if view_count is not None:
            self.view_count = view_count

    def is_valid_github_repo(self):
        parsed = urlparse(self.url)
        return parsed.netloc == "github.com" and len(parsed.path.strip("/").split("/")) == 2

    def get_recent_logs(self, n=5):
        return self.logs[-n:]

    def encode_url(self):
        return base64.b64encode(self.url.encode()).decode()

    def decode_url(self, encoded_url: str):
        return base64.b64decode(encoded_url.encode()).decode()

    def export_logs_json(self):
        return json.dumps({
            "timestamp": datetime.now().isoformat(),
            "logs": self.logs,
            "summary": self.summary_report()
        }, indent=2)

if __name__ == "__main__":
    booster = GitHubViewBooster("https://github.com/yourusername/yourrepo", 10)

    if booster.validate_url() and booster.is_valid_github_repo():
        booster.send_fake_views()
        booster.save_report()
        booster.hide_report_file()
