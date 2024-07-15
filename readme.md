# To run this script:

1. Create a virtural environment: python -m venv myenv
2. Activate the virtual invironment
3. Install dependencies: pip install -r requirements.txt
4. rename example.env to .env and put in your credentials
5. On line 144 put the url you want to scrape
6. run the script with: pytest linkedin_scrapper.py --user-data-dir=data --rs --reruns=2