import json
from urllib import request
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Payments, Collections
from .serializers import (
    PaymentsSerializer,
    CollectionsSerializer,
    CollectionsCardSerializer,
    NameEnquirySerializer,
)
from .services import PeoplesPayService
from django.core.paginator import Paginator, EmptyPage
import requests
import uuid


class TokenView(APIView):
    def get(self, request):
        token = PeoplesPayService.get_token()

        if token:
            return Response({"token": token}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"message": "Failed to retrieve token"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class PaymentsView(APIView):
    def post(self, request):
        payment_serializer = PaymentsSerializer(data=request.data)
        # Get the token using the PeoplesPayService from the .get_token() method
        print(payment_serializer, "payment serializer")
        token = PeoplesPayService.get_token(operation="CREDIT")
        print(token, "token")
        if token is None:
            return Response(
                {"message": "Failed to retrieve token"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if payment_serializer.is_valid():
            validated_data = payment_serializer.validated_data
            print(validated_data, "validated data")
        # Disburse payment
        disburse_payload = {
            "amount": str(validated_data["amount"]),
            "account_number": validated_data["account_number"],
            "account_name": validated_data["account_name"],
            "account_issuer": validated_data["account_issuer"],
            # "external_transaction_id": validated_data["external_transaction_id"],
            "description": validated_data["description"],
        }
        disburse_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token['data']}",
        }
        print(disburse_payload, "Disburse payload")

        try:
            disburse_response = requests.post(
                f"{PeoplesPayService.BASE_URL}/disburse",
                json=disburse_payload,
                headers=disburse_headers,
            )
            disburse_data = disburse_response.json()
            print(disburse_data, "disburse_data")

            if disburse_response.status_code == 200 and disburse_data.get("success"):
                payment_serializer.save()  # Save payment record to the database
                return Response(
                    {"message": "Payment processed successfully"},
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {"message": disburse_data.get("message", "Payment failed")},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except requests.exceptions.RequestException as e:
            return Response(
                {"message": f"Error processing payment: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CollectionsView(APIView):
    def post(self, request):
        collection_serializer = CollectionsSerializer(data=request.data)
        # transaction_id = request.data.get("transactionId")

        # Generate the external_transaction_id at the start
        external_transaction_id = uuid.uuid4()
        print("take a look")

        if collection_serializer.is_valid():
            print("if passed")
            validated_data = collection_serializer.validated_data

            # Assign the external_transaction_id to the validated data after it is available
            validated_data["external_transaction_id"] = external_transaction_id

            # Get the token using the PeoplesPayService
            token = PeoplesPayService.get_token()
            print(token)
            if token is None:
                return Response(
                    {"message": "Failed to retrieve token"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Process the collection
            collection_payload = {
                "amount": str(validated_data["amount"]),
                "account_number": validated_data["account_number"],
                "account_name": validated_data["account_name"],
                "account_issuer": validated_data["account_issuer"],
                "callbackUrl": validated_data["callbackUrl"],
                "description": validated_data["description"],
                "externalTransactionId": str(external_transaction_id),
            }
            collection_headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token['data']}",
            }

            try:
                print(collection_payload, "trying to send collection")
                collection_response = requests.post(
                    f"{PeoplesPayService.BASE_URL}/collectmoney",
                    json=collection_payload,
                    headers=collection_headers,
                )
                collection_data = collection_response.json()
                print(collection_data, "collection data")

                # extract the PeoplesPay ID if available in the response
                transaction_id = collection_data.get("transactionId")

                if (
                    collection_response.status_code == 200
                    and collection_data.get("success")
                    and transaction_id
                ):
                    # Save collection record, including external_transaction_id and PeoplesPay ID
                    collection_serializer.save(
                        external_transaction_id=external_transaction_id,
                        transaction_id=transaction_id,  # Save the PeoplesPay ID
                    )
                    # Create a corresponding payment entry with the same external_transaction_id
                    Payments.objects.create(
                        external_transaction_id=external_transaction_id,
                        amount=validated_data["amount"],
                        account_name=validated_data["account_name"],
                        account_number=validated_data["account_number"],
                        account_issuer=validated_data["account_issuer"],
                    )
                    return Response(
                        {
                            "message": collection_data["message"],
                            "internal_id": str(
                                external_transaction_id
                            ),  # Internal ID for tracking
                            "peoplespay_id": collection_data[
                                "transactionId"
                            ],  # PeoplesPay ID
                            "collectin_status": collection_data["success"],
                            "collection_code": collection_data["code"],
                        },
                        status=status.HTTP_201_CREATED,
                    )

                else:
                    return Response(
                        {
                            "message": collection_data.get(
                                "message", "Collection failed"
                            )
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            except requests.exceptions.RequestException as e:
                return Response(
                    {"message": f"Error processing collection: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(
            collection_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )


# Helper function to check peoples pay for payment status
def check_peoplespay_status(transaction_id):
    url = f"{PeoplesPayService.BASE_URL}"
    print(request, "looking at peoplespay")
    token = PeoplesPayService.get_token()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token['data']}",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get(
            "status"
        )  # Extract and return the status field from the response
    return Response({request.get("success", "code", "message")})


# Working version of callback


class PaymentCallbackAPIView(APIView):
    def post(self, request):
        # Extract PeoplesPay transaction ID and success status from the request data
        transaction_id = request.data.get("transactionId")

        # payment_success = request.data.get("success")

        # incoming data from PeoplesPay for debugging
        print("Incoming request data:", json.dumps(request.data, indent=4))
        # Validate incoming data

        """
        if not transaction_id or payment_success is None:
        """
        if not transaction_id:
            return Response(
                {"error": "Missing required fields: transactionId"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Convert payment_success to a proper boolean value
        # payment_success = True if payment_success in [True, "true", "True"] else False

        # Find the collection related to this transaction using transaction_id

        try:
            collection = Collections.objects.get(transaction_id=transaction_id)
            print(collection, "collection data")

            # Update the transaction status based on the success value
            # if payment_success:
            #     collection.transaction_status = "completed"
            # else:
            #     collection.transaction_status = "failed"
            # collection.save()

            # Return a response with updated information
            return Response(
                {
                    "message": request.data.get("message"),
                    "transaction_id": request.data.get("transactionId"),
                    "external_transaction_id": collection.external_transaction_id,
                    "amount": collection.amount,
                    "status": collection.transaction_status,
                    "account_name": collection.account_name,
                    "description": collection.description,
                    "created_at": collection.created_at,
                },
                status=status.HTTP_200_OK,
            )
        except Collections.DoesNotExist:
            return Response(
                {"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND
            )


class NameEnquiryView(APIView):
    def post(self, request):
        serializer = NameEnquirySerializer(data=request.data)
        token = PeoplesPayService.get_token()
        if serializer.is_valid():
            data = serializer.validated_data
            enquiry_payload = {
                "account_type": data["account_type"],
                "account_number": data["account_number"],
                "account_issuer": data["account_issuer"],
            }
            print(enquiry_payload, "enquiry payload")
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token['data']}",
            }
            print(headers, "headers")
            try:
                response = requests.post(
                    f"{PeoplesPayService.BASE_URL}/enquiry",
                    json=enquiry_payload,
                    headers=headers,
                )
                response_data = response.json()
                print(response_data, "response data")
                if response.status_code == 200 and response_data.get("success"):
                    return Response(
                        {
                            "message": "Enquiry processed successfully",
                            "data": response_data["data"],
                        },
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {
                            "error": response_data.get("message", "Enquiry failed"),
                            "code": response_data.get("code"),
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except requests.exceptions.RequestException as e:
                return Response(
                    {"error": f"Error processing enquiry: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CardPaymentAPIView(APIView):
    def post(self, request):
        print("Received request:", request.data)  # Debug incoming request data

        card_serializer = CollectionsCardSerializer(data=request.data)
        external_transaction_id = uuid.uuid4()

        if card_serializer.is_valid():
            print("Serializer is valid.")  # Debug serializer validation
            validated_data = card_serializer.validated_data
            print("Validated data:", validated_data)  # Debug validated data

            # Assign the external_transaction_id
            validated_data["external_transaction_id"] = external_transaction_id

            # Get the token using PeoplesPayService
            token = PeoplesPayService.get_token()
            print("Retrieved token:", token)  # Debug token retrieval

            if token is None:
                return Response(
                    {"message": "Failed to retrieve token"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Prepare the payload
            card_payload = {
                "account_name": validated_data["account_name"],
                "amount": validated_data["amount"],
                "card": validated_data["card"],
                "description": validated_data["description"],
                "callbackUrl": validated_data["callbackUrl"],
                "clientRedirectUrl": validated_data["clientRedirectUrl"],
            }
            print("Payload prepared for PeoplesPay:", card_payload)  # Debug payload

            collection_headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token['data']}",
            }
            print(
                "Headers for PeoplesPay request:", collection_headers
            )  # Debug headers

            try:
                card_response = requests.post(
                    f"{PeoplesPayService.BASE_URL}/collectmoney/card",
                    json=card_payload,
                    headers=collection_headers,
                )
                print(
                    "Response from PeoplesPay:", card_response.text
                )  # Debug raw response

                card_data = card_response.json()
                print(
                    "Parsed response data from PeoplesPay:", card_data
                )  # Debug parsed JSON

                card_transaction_id = card_data.get("transactionId")
                print(
                    "Extracted card_transaction_id:", card_transaction_id
                )  # Debug transaction ID

                if (
                    card_response.status_code == 200
                    and card_data["success"]
                    and card_transaction_id
                ):
                    print(
                        "Transaction successful. Saving record..."
                    )  # Debug success case

                    # Save validated data
                    card_serializer.save(
                        external_transaction_id=external_transaction_id,
                        card_transaction_id=card_transaction_id,
                    )
                    print("Record saved in database.")  # Debug successful save

                    return Response(
                        {
                            "message": "Collection processed successfully",
                            "external_transaction_id": str(external_transaction_id),
                            "card_transaction_id": card_transaction_id,
                            "collection_status": card_data["success"],
                            "redirect_url": card_data["redirectUrl"],
                        },
                        status=status.HTTP_201_CREATED,
                    )
                else:
                    print(
                        "Transaction failed. PeoplesPay response:",
                        card_data.get("message", "Unknown error"),
                    )  # Debug failure case
                    return Response(
                        {"message": card_data.get("message", "Transaction failed")},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            except requests.exceptions.RequestException as e:
                print("Error during PeoplesPay request:", str(e))  # Debug request error
                return Response(
                    {"message": f"Error processing collection: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        else:
            print(
                "Serializer is invalid. Errors:", card_serializer.errors
            )  # Debug serializer errors
            return Response(card_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# getting transaction status of a specific transaction from peoplespay
class TransactionsViewById(APIView):
    def get(self, request, transaction_id):
        # Check if the transaction exists in the database
        try:
            transaction = Collections.objects.get(transaction_id=transaction_id)
            print(transaction, "transaction")
        except Collections.DoesNotExist:
            return Response(
                {"error": "Transaction not found in local database"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Get PeoplesPay token
        token = PeoplesPayService.get_token()
        print(token, ":token")
        if not token:
            return Response(
                {"message": "Failed to retrieve token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # PeoplesPay API URL
        url = f"https://peoplespay.com.gh/peoplepay/transactions/get/{transaction_id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token['data']}",
        }

        peoplespay_response = requests.get(url, headers=headers)
        if peoplespay_response.status_code != 200:
            return Response(
                {"error": "Failed to retrieve transaction from PeoplesPay"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = peoplespay_response.json()
        print("PeoplesPay response data:", data)
        peoples_pay_status = data.get("data", {}).get("status")
        print("PeoplesPay status:", peoples_pay_status)

        # If status is pending, do not update local database
        if peoples_pay_status == "pending":
            return Response(
                {
                    "message": "Transaction is still pending",
                    "transaction_id": transaction_id,
                    "status": peoples_pay_status,
                },
                status=status.HTTP_200_OK,
            )

        # status is "failed" or "paid", update local database
        elif peoples_pay_status in ["failed", "paid"]:
            transaction.transaction_status = peoples_pay_status
            transaction.save()
            print(transaction, "transaction")
            return Response(
                {
                    "message": f"Transaction status updated to {peoples_pay_status}",
                    "transaction_id": transaction_id,
                    "peoplespay_data_status": data.get("status"),
                    # "status": peoples_pay_status,
                    "peoplespay_data": data,
                    # "peoplespay_data_message": data.get("message"),
                },
                status=status.HTTP_200_OK,
            )
        else:
            # Log unexpected status for debugging
            print(f"Unexpected status from PeoplesPay: {peoples_pay_status}")
            return Response(
                {
                    "message": f"Unknown status from PeoplesPay: {peoples_pay_status}",
                    "transaction_id": transaction_id,
                    "peoplespay_data": data,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

# get 50 most recent transactions from collcections from local database
class TransactionsView(APIView):
    def get(self, request):
        try:
            # fetch transactions from the database filtered by created_at
            transactions_data = Collections.objects.all().order_by("-created_at")
            print(transactions_data, "transactions_data")

            # paginate the transactions
            page_number = request.query_params.get("page", 1)
            page_size = request.query_params.get("page_size", 50)

            # validate the page size, ensure they are positive integers
            try:
                page_size = int(page_size)
                if page_size <= 0:
                    raise ValueError("Page size must be a positive integer")
            except ValueError as e:
                page_size = 50 # fallback to default page size
                print(f"Invalid page size: {e}")

            paginator = Paginator(transactions_data, page_size)

            try:
                # get requested page
                page_obj = paginator.page(page_number)
            except EmptyPage:
                return Response(
                    {"error": "Page does not exist"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            serialzer = CollectionsSerializer(page_obj, many=True)

            # return paginated data
            return Response(
                {
                    "message": "Transactions retrieved successfully",
                    "data": serialzer.data,
                    "pagination": {
                        "current_page": page_obj.number,
                        "total_pages": paginator.num_pages,
                        "total_items": paginator.count,
                        "page_size": page_size,
                        "has_next": page_obj.has_next(),
                        "has_previous": page_obj.has_previous(),
                    },
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "error": f"An unexpected error occurred: {str(e)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# for updating payment status message

# class PaymentCallbackAPIView(APIView):
#     def post(self, request):
#         transaction_id = request.data.get("transactionId")
#         payment_success = request.data.get("success")
#         response_code = request.data.get("code")

#         # Validate incoming data
#         if not transaction_id or response_code is None:
#             return Response(
#                 {"error": "Missing required fields: transactionId"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         try:
#             # Retrieve the collection using the transaction ID
#             collection = Collections.objects.get(external_transaction_id=transaction_id)

#             # Determine the status based on response code
#             if (
#                 response_code == "00"
#             ):  # Adjust the code as per PeoplesPay's documentation
#                 updated_status = "completed"
#             elif response_code in [
#                 "02",
#                 "03",
#             ]:  # Example failure codes; adjust as needed
#                 updated_status = "failed"
#             elif response_code == "01":  # '01' means still processing
#                 updated_status = "pending"
#             else:
#                 updated_status = (
#                     collection.transaction_status
#                 )  # Keep current status if unknown code

#             # Update the collection status only if necessary
#             if updated_status != collection.transaction_status:
#                 collection.transaction_status = updated_status
#                 collection.save()

#             return Response(
#                 {
#                     "message": "Callback processed successfully",
#                     "transaction_id": collection.external_transaction_id,
#                     "amount": collection.amount,
#                     "status": collection.transaction_status,
#                     "account_name": collection.account_name,
#                     "description": collection.description,
#                     "created_at": collection.created_at,
#                 },
#                 status=status.HTTP_200_OK,
#             )

#         except Collections.DoesNotExist:
#             return Response(
#                 {"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND
#             )
#         except Exception as e:
#             return Response(
#                 {"error": "An unexpected error occurred", "details": str(e)},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )
