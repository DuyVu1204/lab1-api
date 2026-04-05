import requests

BASE_URL = "http://127.0.0.1:8000"

TEST_CASES = [
	"""New York (CNN)When Liana Barrientos was 23 years old, she got married in Westchester County, New York.
A year later, she got married again in Westchester County, but to a different man and without divorcing her first husband.
Only 18 days after that marriage, she got hitched yet again. Then, Barrientos declared \"I do\" five more times, sometimes only within two weeks of each other.
In 2010, she married once more, this time in the Bronx. In an application for a marriage license, she stated it was her \"first and only\" marriage.
Barrientos, now 39, is facing two criminal counts of \"offering a false instrument for filing in the first degree,\" referring to her false statements on the
2010 marriage license application, according to court documents.
Prosecutors said the marriages were part of an immigration scam.
On Friday, she pleaded not guilty at State Supreme Court in the Bronx, according to her attorney, Christopher Wright, who declined to comment further.
After leaving court, Barrientos was arrested and charged with theft of service and criminal trespass for allegedly sneaking into the New York subway through an emergency exit, said Detective
Annette Markowski, a police spokeswoman. In total, Barrientos has been married 10 times, with nine of her marriages occurring between 1999 and 2002.
All occurred either in Westchester County, Long Island, New Jersey or the Bronx. She is believed to still be married to four men, and at one time, she was married to eight men at once, prosecutors say.
Prosecutors said the immigration scam involved some of her husbands, who filed for permanent residence status shortly after the marriages.
Any divorces happened only after such filings were approved. It was unclear whether any of the men will be prosecuted.
The case was referred to the Bronx District Attorney\'s Office by Immigration and Customs Enforcement and the Department of Homeland Security\'s
Investigation Division. Seven of the men are from so-called \"red-flagged\" countries, including Egypt, Turkey, Georgia, Pakistan and Mali.
Her eighth husband, Rashid Rajput, was deported in 2006 to his native Pakistan after an investigation by the Joint Terrorism Task Force.
If convicted, Barrientos faces up to four years in prison. Her next court appearance is scheduled for May 18.""",
	"""Artificial intelligence is changing how doctors, teachers, and engineers work every day. In hospitals, machine learning systems can help analyze scans, detect patterns, and support early diagnosis, but they still require human review to avoid mistakes. In schools, adaptive learning tools can personalize lessons for students with different strengths and weaknesses, giving teachers more time to focus on guidance and feedback. In transportation, automated systems can improve traffic flow, predict maintenance needs, and reduce delays. Even so, every one of these uses needs clear rules, testing, and human oversight before it can be trusted at scale.""",
	"""A community library in a small town can become a center for learning, creativity, and social connection. Students use it for homework, quiet reading, and research projects, while adults attend workshops on digital skills, job searching, and financial planning. Volunteers organize book drives, reading clubs, and weekend events for children, helping the library stay active beyond school hours. When local leaders invest in libraries, the result is not only access to books but also stronger participation, better literacy, and a more connected neighborhood.""",
]


def _check_health() -> None:
	try:
		health = requests.get(f"{BASE_URL}/health", timeout=10)
		health.raise_for_status()
	except requests.RequestException:
		print("API chưa sẵn sàng. Hãy chạy: uvicorn main:app --reload")
		print("Nếu mới chạy lần đầu, model sẽ tải khá lâu. Đợi server báo startup complete rồi test lại.")
		raise SystemExit(1)


def test_get_root() -> None:
	"""Test GET / endpoint."""
	try:
		response = requests.get(f"{BASE_URL}/", timeout=10)
		response.raise_for_status()
		data = response.json()
		print(f"[PASS] GET /")
		print(f"  Model: {data.get('model')}")
		print(f"  Endpoints count: {len(data.get('endpoints', {}))}")
		print()
	except requests.RequestException as exc:
		print(f"[FAIL] GET / -> {exc}")
		print()


def test_get_health() -> None:
	"""Test GET /health endpoint."""
	try:
		response = requests.get(f"{BASE_URL}/health", timeout=10)
		response.raise_for_status()
		data = response.json()
		print(f"[PASS] GET /health")
		print(f"  Status: {data.get('status')}")
		print(f"  Model loaded: {data.get('model_loaded')}")
		print()
	except requests.RequestException as exc:
		print(f"[FAIL] GET /health -> {exc}")
		print()


def main() -> None:
	predict_url = f"{BASE_URL}/predict"
	_check_health()

	print("=== Test API Endpoints ===")
	print()

	test_get_root()
	test_get_health()

	print(f"Bắt đầu test {len(TEST_CASES)} POST /predict...")
	for index, text in enumerate(TEST_CASES, start=1):
		payload = {"text": text}
		try:
			response = requests.post(predict_url, json=payload, timeout=120)
			response.raise_for_status()
			data = response.json()
			summary = (data.get("summary") or "").strip()
			if summary:
				print(f"[PASS] POST /predict - Case {index}")
				print(summary)
				print()
			else:
				print(f"[FAIL] Case {index}: response không có summary hợp lệ")
		except requests.RequestException as exc:
			print(f"[FAIL] Case {index}: request error -> {exc}")


if __name__ == "__main__":
	main()