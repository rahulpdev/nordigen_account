from typing import Dict, Union, List, Optional, Tuple
from requests.exceptions import HTTPError
from nordigen import NordigenClient


def create_nordigen_client(
        secret_id: str, secret_key: str, refresh_token: Optional[str] = None
) -> Tuple[NordigenClient, str]:
    """
    Create and configure a NordigenClient instance using either a refresh token or by generating a new access token.

    Args:
        secret_id (str): Nordigen API secret ID.
        secret_key (str): Nordigen API secret key.
        refresh_token (str, optional): Refresh token to obtain the access token.

    Returns:
        Tuple[NordigenClient, Optional[str]]: Configured Nordigen client instance and the new refresh token if generated, else None.

    Raises:
        NordigenAPIError: If token generation or exchange fails.
    """
    status_invalid = 401  # HTTP status code for unauthorized access
    new_refresh_token = None
    client = NordigenClient(secret_id=secret_id, secret_key=secret_key)

    try:
        if not refresh_token:
            # Generate new tokens if no refresh token is provided
            token_data = client.generate_token()
            new_refresh_token = token_data["refresh"]  # Capture the new refresh token
        else:
            try:
                # Exchange the provided refresh token for an access token
                token_data = client.exchange_token(refresh_token)
            except HTTPError as http_err:
                response_data = http_err.response.json()
                status_code = response_data.get("status_code")

                if status_code == status_invalid:
                    # If refresh token is expired, generate a new token
                    token_data = client.generate_token()
                    new_refresh_token = token_data["refresh"]
                else:
                    raise NordigenAPIError(
                        message=f"Error exchanging token: {response_data}",
                        status_code=status_code,
                        response_body=response_data,
                    )

        # Extract and set the access token
        access_token = token_data["access"]
        client.token = access_token

        return client, new_refresh_token

    except KeyError as key_err:
        raise NordigenAPIError(
            message=f"Missing expected key in token response: {str(key_err)}"
        )

    except HTTPError as http_err:
        response_data = http_err.response.json()
        status_code = response_data.get("status_code")
        raise NordigenAPIError(
            message=f"Error generating token: {response_data}",
            status_code=status_code,
            response_body=response_data,
        )

    except Exception as e:
        raise NordigenAPIError(
            message=f"Unexpected error obtaining access token: {str(e)}"
        )


class NordigenAPIError(Exception):
    """Custom exception for errors related to the Nordigen API."""

    def __init__(
            self, message: str, status_code: Optional[int] = None, response_body: Optional[Dict] = None
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class BankAccount:
    """Representation of a Bank Account."""

    DetailsApiResponseType = Dict[
        str, Dict[str, str]
    ]  # Type alias for account details API response
    BalancesApiResponseType = Dict[
        str, List[Dict[str, Union[Dict[str, str], str, bool]]]
    ]  # Type alias for account balances API response

    def __init__(
            self, client: NordigenClient, account_id: str, fetch_data: bool = False
    ) -> None:
        """
        Initialize a BankAccount object.

        Args:
            client (NordigenClient): An authenticated Nordigen client instance.
            account_id (str): The unique account ID.
            fetch_data (bool): Whether to fetch account details and balances on initialization.
        """
        self._client = client
        self._account_id = account_id

        # Initialize placeholders for account and balance data
        self.name = None
        self.status = None
        self.currency = None
        self.balances: List[Dict[str, Union[str, float]]] = []

        # Fetch data if the flag is set
        if fetch_data:
            self.update_account_data()
            self.update_balance_data()

    def update_account_data(self) -> None:
        """
        Fetch and update basic account details.

        Raises:
            NordigenAPIError: If there is an error retrieving account details.
        """
        try:
            details_response: BankAccount.DetailsApiResponseType = self._client.account_api(id=self._account_id).get_details()
            account_details = details_response.get("account", {})

            # Extract and store account details
            self.name = account_details.get("name", "Unknown")
            self.status = account_details.get("status", "Unknown")
            self.currency = account_details.get("currency", "Unknown")

        except HTTPError as http_err:
            response_data = http_err.response.json()
            status_code = response_data.get("status_code")
            raise NordigenAPIError(
                message=f"Error retrieving account details: {response_data}",
                status_code=status_code,
                response_body=response_data,
            )

        except Exception as e:
            raise NordigenAPIError(
                message=f"Unexpected error while fetching account details: {str(e)}"
            )

    def update_balance_data(self) -> None:
        """
        Fetch and update balance information.

        Raises:
            NordigenAPIError: If there is an error retrieving account balances.
        """
        try:
            balances_response: BankAccount.BalancesApiResponseType = self._client.account_api(id=self._account_id).get_balances()
            self.balances = []  # Reset balances
            account_balances = balances_response.get("balances", [])

            # Parse and store balance data
            for balance in account_balances:
                balance_data = {
                    "balanceType": balance.get("balanceType", "Unknown"),
                    "amount": float(balance.get("balanceAmount", {}).get("amount", 0.00)),
                    "currency": balance.get("balanceAmount", {}).get("currency", "Unknown"),
                }
                self.balances.append(balance_data)

        except HTTPError as http_err:
            response_data = http_err.response.json()
            status_code = response_data.get("status_code")
            raise NordigenAPIError(
                message=f"Error retrieving account balances: {response_data}",
                status_code=status_code,
                response_body=response_data,
            )

        except Exception as e:
            raise NordigenAPIError(
                message=f"Unexpected error while fetching account balances: {str(e)}"
            )


class BankAccountManager:
    """Manager for handling multiple bank accounts."""

    STATUS_EXPIRED = "EX"  # Requisition status indicating expiration

    RequisitionApiResponseType = Dict[
        str, Union[str, List[str], None, bool]
    ]  # Type alias for requisition API response

    def __init__(
            self, client: NordigenClient, requisition_id: str, fetch_data: bool = False
    ) -> None:
        """
        Initialize a BankAccountManager.

        Args:
            client (NordigenClient): An authenticated Nordigen client instance.
            requisition_id (str): The requisition ID to fetch linked accounts.
            fetch_data (bool): Whether to fetch account details and balances for all accounts on initialization.
        """
        self._client = client
        self._requisition_id = requisition_id
        self.accounts = []  # List to hold BankAccount objects
        self.institution_id = None
        self.reference = None

        # Pass fetch_data to _initialize_accounts
        self._initialize_accounts(fetch_data)

    def _initialize_accounts(self, fetch_data: bool) -> None:
        """
        Initialize BankAccount objects for all linked accounts.

        Args:
            fetch_data (bool): Whether to fetch account details and balances on initialization of BankAccount object.

        Raises:
            NordigenAPIError: If there is an error with the requisition or account data retrieval.
        """
        try:
            accounts_response = self._client.requisition.get_requisition_by_id(
                requisition_id=self._requisition_id
            )

            self.institution_id = accounts_response.get("institution_id")
            self.reference = accounts_response.get("reference")

            # Check if the requisition status is expired
            account_status = accounts_response.get("status")
            if account_status == self.STATUS_EXPIRED:
                raise NordigenAPIError(
                    message="Access to accounts has expired as set in End User Agreement. Connect the accounts again with a new requisition.",
                    status_code=428,
                    response_body=accounts_response,
                )

            # Retrieve list of account IDs linked to the requisition
            account_ids = accounts_response.get("accounts", [])
            if not account_ids:
                raise NordigenAPIError(
                    message="No accounts found for the given requisition ID. Ensure that bank authorization has been completed.",
                    status_code=410,
                    response_body=accounts_response,
                )

            # Initialize a BankAccount instance for each account ID
            for account_id in account_ids:
                self.accounts.append(BankAccount(self._client, account_id, fetch_data=fetch_data))

        except HTTPError as http_err:
            response_data = http_err.response.json()
            status_code = response_data.get("status_code")
            raise NordigenAPIError(
                message=f"Error fetching requisition details: {response_data}",
                status_code=status_code,
                response_body=response_data,
            )

        except Exception as e:
            raise NordigenAPIError(
                message=f"Unexpected error during requisition initialization: {str(e)}"
            )
