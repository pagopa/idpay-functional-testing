# Merchant and Barcode Payment Flow

## Actors

- **Citizen:** onboards to an initiative, then creates a barcode payment.
- **Merchant:** owns one or more points of sale and is identified on payment
  requests by its merchant ID.
- **Point of sale (POS):** accepts the barcode. Each POS has its own Keycloak
  client credentials.

## Authentication and Authorization

1. The POS obtains an OAuth 2.0 access token using the Keycloak
   client-credentials grant.
2. The access token's claims identify the POS; no POS identifier header is
   required.
3. The POS authorizes the barcode payment through the Merchant E-commerce APIM
   endpoint with the Bearer token, plus the merchant ID and acquirer ID
   headers.

## Bonus Elettrodomestici Test Flow

1. Create a citizen fiscal code and configure its ISEE declaration.
2. Submit onboarding and poll until the asynchronous status is
   `ONBOARDING_OK`.
3. Create a barcode payment as the onboarded citizen.
4. Obtain a token for the merchant's selected POS.
5. Authorize the barcode payment as that POS and assert the transaction is
   `AUTHORIZED`.
6. Capture the authorized barcode payment as that POS and assert the
   transaction is `CAPTURED`.
7. Upload an invoice file and document number for the captured payment as that
   POS.
8. Upload an invoice file and document number for an already invoiced payment
   as that POS.

The Bonus authorization payload requires
`additionalProperties.productGtin`. The approved test value is
`TUMBLEDRYERS03`.

## Test Configuration

Keep credentials only in the ignored environment secrets file. Configure a
Merchant E-commerce APIM's base URL is also environment-specific; for the dev
environment it starts with
`https://api-io.dev.cstar.pagopa.it/idpay-itn/merchant-ecommerce`. Configure
it and the merchant's POS credentials under:

```json
{
  "base_path": {
    "MERCHANT_ECOMMERCE": "<MERCHANT_ECOMMERCE_APIM_BASE_PATH>"
  },
  "merchants": {
    "merchant_1": {
      "points_of_sale": {
        "pos_1": {
          "client_credentials": {
            "token_url": "<KEYCLOAK_POINT_OF_SALE_TOKEN_URL>",
            "client_id": "<KEYCLOAK_POINT_OF_SALE_CLIENT_ID>",
            "client_secret": "<KEYCLOAK_POINT_OF_SALE_CLIENT_SECRET>"
          }
        }
      }
    }
  }
}
```
