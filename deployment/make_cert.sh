#!/bin/bash
set -eu
if [ "$#" -ne 1 ]; then
  echo "Usage: $0 domain.example.com"
  echo
  echo "Generates a private key and a default CSR which you can send to" \
       "your CA. It prompts later for the certificate and stores it in a" \
       "reasonable place."
  echo "Tested only with StartSSL."
  exit 1
fi
DOMAIN="$1"

copy_clipboard() {
  if which xclip > /dev/null 2>&1; then
    xclip -selection clipboard
  else
    cat > /dev/null
  fi
}

umask 0077
KEY_FILE="/tmp/${DOMAIN}.key"
CERT_FILE="/tmp/${DOMAIN}.pem"

openssl genrsa -out "${KEY_FILE}" 4096

echo "Paste the following CSR to your CA:"
echo
openssl req -new -batch -key "${KEY_FILE}" | tee >(copy_clipboard)
echo

echo "Once you receive the certificate, paste it here:"
echo "(End input with new line plus Ctrl+D)"
cat > "${CERT_FILE}"

echo "Enqueueing..."
cat $KEY_FILE $CERT_FILE | ./sslman.py --ca 'startssl' --enqueue "$DOMAIN"
echo "Certificate enqueued successfully!"
