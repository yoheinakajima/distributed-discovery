# Cryptographic holdout custody

This is a future protocol, not an active custody operation. No private seed,
key, holdout, answer key, ciphertext, or custodian exists.

## Authorized future sequence

1. Commit the offline generator and independent verifier.
2. Freeze exact provider/model, prompt, schema, evaluator, and execution
   configuration versions.
3. Generate a seed with an operating-system CSPRNG inside an approved isolated
   environment.
4. Publish `SHA-256("DiscoveryBench Agents v1 seed commitment\0" || seed)`.
5. Generate the predeclared holdout batches.
6. Encrypt instances and answer keys separately with an established
   authenticated-encryption implementation: XChaCha20-Poly1305 from libsodium
   or AES-256-GCM from a maintained cryptographic library.
7. Record algorithm, nonce, associated-data, ciphertext, and manifest hashes.
8. Restrict the evaluator runtime to ciphertext access and log every access.
9. Execute only frozen configurations.
10. Make raw outputs append-only and commit their hashes.
11. Unseal only after every scheduled output is immutable.
12. Verify seed, ciphertext, answer-key, configuration, and trace commitments.
13. Evaluate through both registered verification methods.
14. Release generator parameters, seeds, and answers only after the result lock
    and only when contamination and licensing review permits.

Keys are never stored beside ciphertext or in Git. Nonces must be unique per
key. Associated data binds benchmark, content, protocol, generator, batch,
artifact type, and schema versions. Commitment comparison uses constant-time
library functions. Encryption and hashing implementations may not be invented
for this project.

The public test vectors in `public-test-vectors/` validate serialization and
SHA-256 commitment logic only. Their fixed seed and toy instance are explicitly
public and cannot become a private holdout.

Stop if a commitment changes, authenticated decryption fails, access is
unlogged, a key is exposed, an answer is opened early, or model/config identity
differs from the frozen manifest. Quarantine the entire affected batch; do not
patch individual records.
