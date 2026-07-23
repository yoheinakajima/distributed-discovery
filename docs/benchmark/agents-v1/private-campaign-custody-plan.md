# Private campaign custody execution plan

This is an ordered future command plan, not an active custody operation.

1. Verify a clean implementation commit and exact model manifest.
2. Validate an active owner authorization against commit, tier, models, caps,
   expiration, custody, trace, and batch IDs.
3. Generate a CSPRNG seed in the authorized secret context; immediately commit
   only its hash.
4. Generate the predeclared sealed batch and answer material from the frozen
   allocation; encrypt task bodies and answer keys separately with AES-256-GCM.
5. Bind associated data to instrument, content, protocol, generator, batch,
   commit, and authorization IDs.
6. Record append-only access logs and ciphertext/commitment manifests.
7. Execute exact models without unsealing answers; lock and hash every output.
8. Verify output locks, then unseal through the registered access event.
9. Run Method A, independent Method B, contamination, and corruptions.
10. Release only permitted redacted artifacts after safety and claim gates.

Stop and quarantine the entire batch on any authorization, commitment,
encryption, access-log, model, output-lock, contamination, or trace mismatch.
This registration creates none of these private objects.
