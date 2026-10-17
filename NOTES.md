# Notes: assumptions and future improvements

## Assumptions and decisions

1. **Member order:** Members receive the pot in the order they are registered.
2. **Group size:** The group needs at least one member before a week can close.
3. **Adding members:** Members can only be added before the first contribution is recorded. This avoids changing the pot amount after a cycle has begun.
4. **Unique names/IDs:** Member names are trimmed and compared without case sensitivity, so `Ama` and `ama` are duplicates.
5. **Partial payments:** Multiple payments can be made for a member during the current week, provided the total does not exceed that member's weekly contribution.
6. **Closing a week:** A week closes only when every registered member has paid the full contribution. An unsuccessful close does not advance the week or create a payout.
7. **Payout amount:** The payout is the fixed weekly contribution multiplied by the number of members.
8. **Money:** Amounts use `Decimal`; values with more than two decimal places are rejected. No binary floating-point arithmetic is used for money.
9. **Payout order:** The first registered member receives week 1's pot, the second receives week 2's pot, and so on.
10. **Persistence:** Data is stored in memory for this first version and disappears when the program exits.

## Improvements with more time

- Save groups, payments, and payout history to SQLite so records survive restarts.
- Add a unique member ID separate from the display name.
- Add dates, receipts, audit logs, and a way to export reports to CSV.
- Add role-based access and backups if real group financial records are stored.
- Add integration tests for persistence and stronger input validation.
- Add a configuration or setup flow for multiple independent groups.
