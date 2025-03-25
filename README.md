## Bank Integration

Unofficial API to handle bank transactions using ERPNext (v11+)

## Prerequisites

Needs [`chromedriver`](https://launchpad.net/ubuntu/bionic/+package/chromium-chromedriver) installed.

## In action

### Authentication

<img src=".github/demo.gif" style="max-width: 100%;">

### Make Payment Now

https://github.com/user-attachments/assets/776285d9-e175-45a4-91ca-955521eca7a8

## Running the App Standalone

To run the app standalone, follow these steps:

1. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```

2. Ensure that `chromedriver` is installed and available in your system's PATH.

3. Run the app:
   ```sh
   python -m bank_integration
   ```

## Providing Payment Data via CSV File

To provide payment data via a CSV file, follow these steps:

1. Create a CSV file named `payment_entries.csv` with the following columns:
   - `name`
   - `account`
   - `paid_amount`
   - `bank_account_no`
   - `bank_name`
   - `username`
   - `password`

2. Populate the CSV file with the payment data.

3. Place the CSV file in the same directory as the app.

4. Run the app as described in the "Running the App Standalone" section.

#### License

MIT
