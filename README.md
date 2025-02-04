# Nordigen Account

A Python package to interact with the Nordigen Bank Account API, allowing users to retrieve and manage bank account 
details and balances.

## Features

- Secure connection to the Nordigen API using `secret_id` and `secret_key`.
- Retrieve bank account details such as name, status, and currency.
- Fetch account balances, including multiple balance types and currencies.
- Manage multiple linked accounts via the `BankAccountManager` class.
- Automatic retrieval of new refresh token when expired.
- Unified error handling using a custom `NordigenAPIError` exception.

## Installation
Ensure Python 3.7+ is installed. To install the package, use:

```bash
pip install nordigen
```

## Generating Credentials

To use this package, you need to obtain credentials from Nordigen, which include:

- `secret_id`
- `secret_key`
- `refresh_token`
- `requisition_id`

Follow these steps to generate the credentials:

1. Go to the Nordigen Bank Account Data API portal:\
   [https://developer.gocardless.com/bank-account-data/overview](https://developer.gocardless.com/bank-account-data/overview)
2. Sign up for an account and log in.
3. Navigate to the **API Keys** section to generate your `secret_id` and `secret_key`.
4. Follow the API documentation steps to create a requisition and obtain a `requisition_id`.  
   The `refresh_token` is retrieved when you generate an access token via the API.

Once you have obtained these credentials, you can use them to connect to the API and fetch your bank account details.  
The `refresh_token` will expire every 30 days and the `requisition_id` every 90 days and must be refreshed.

## Usage

### 1. Instantiate the Nordigen Client

Use the `create_nordigen_client` function to instantiate the Nordigen client with the required credentials.  
You can pass an optional refresh token, but if not provided, the function will attempt to generate a new one using the 
provided `secret_id` and `secret_key`.

```python
from nordigen_account import create_nordigen_client

# Replace with your actual credentials
secret_id = "your-secret-id"
secret_key = "your-secret-key"
refresh_token = "your-refresh-token"  # Optional

client, new_refresh_token = create_nordigen_client(secret_id, secret_key, refresh_token)
```

If your refresh token has expired, the function will automatically generate a new one.  
The function will return a tuple containing the client instance and a new `refresh_token` if generated, or `None` if 
the existing token is still valid.  

**Handling refresh tokens:**  
If a new `refresh_token` is generated, make sure to update your stored credentials for subsequent API requests.

```python
client, new_refresh_token = create_nordigen_client(secret_id, secret_key, refresh_token)

if new_refresh_token:
    print("New refresh token generated:", new_refresh_token)
    # Store the new token securely for future API requests

```

### 2. Manage Multiple Accounts

The `BankAccountManager` class manages multiple bank accounts linked to a requisition ID.  
When you instantiate `BankAccountManager`, it automatically initializes instances of the `BankAccount` class for each 
linked account.  

```python
from nordigen_account import BankAccountManager

requisition_id = "your-requisition-id"

# Instantiate account manager
manager = BankAccountManager(client, requisition_id, fetch_data=True)

# Access account details
for account in manager.accounts:
   print("Account ID:", account._account_id)
   print("Balances:", account.balances)
```
By default `BankAccount` data is not collected when you initialize `BankAccountManager`. To optionally collect account 
data, set the `fetch_data` flag to True.

### 3. Data Properties
Two data sets are currently supported:

1. Account details
- currency
- status
- name
2. Account balances data
- balanceType
- currency
- amount

To access / refresh each data set use the following commands:

```python
for account in manager.accounts:
   account.update_account_data()
   account.update_balance_data()
```

### 4. Error handling

All errors related to the Nordigen API or account management are raised as a `NordigenAPIError`. This exception provides:
- A descriptive error message.
- The HTTP status code (if available).
- The API response body for debugging.

#### Example:

```python
from nordigen_account import NordigenAPIError

try:
    account.update_balance_data()
except NordigenAPIError as e:
    print(f"Error: {e.message}")
    if e.status_code:
        print(f"HTTP Status Code: {e.status_code}")
    if e.response_body:
        print(f"Response Body: {e.response_body}")
```

This unified error handling makes it easier to debug issues and ensures consistent error reporting throughout the library.

## Project Structure

```
nordigen_account/
|-- nordigen_account/
|  |-- __init__.py        # Core functionality and class definitions
|-- setup.py              # Package configuration for distribution
|-- requirements.txt      # Dependencies
|-- LICENSE               # License information
|-- README.md             # Project documentation
|-- MANIFEST.in           # Package manifest
```

## Dependencies

The package requires the following dependency:

- `nordigen` – Python client for Nordigen API.

The dependency is listed in the `requirements.txt` file.

## Setup for Development

To set up the project locally:

1. Clone the repository:

   ```bash
   git clone https://github.com/rahulpdev/nordigen_account.git
   cd nordigen_account
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run tests or explore the package functionality.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new feature branch.
3. Commit your changes.
4. Push the branch and open a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Rahul Parmar**\
[GitHub Profile](https://github.com/rahulpdev)

---

For more details on the Nordigen API, visit their 
[official documentation](https://developer.gocardless.com/bank-account-data/overview).
