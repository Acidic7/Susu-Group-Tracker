"""Command-line Susu Group Tracker.

Uses Decimal for exact GHS amounts. Data is held in memory for this version.
"""
from decimal import Decimal, InvalidOperation
from dataclasses import dataclass, field
from typing import Dict, List


CENT = Decimal("0.01")


def money(value) -> Decimal:
    """Convert a value to a two-decimal-place Decimal without float arithmetic."""
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError("Enter a valid monetary amount.") from None
    if not amount.is_finite():
        raise ValueError("Amount must be a finite number.")
    if amount != amount.quantize(CENT):
        raise ValueError("Amounts must have no more than two decimal places.")
    return amount.quantize(CENT)


def format_ghs(amount: Decimal) -> str:
    return f"GHS {amount:.2f}"


@dataclass
class Member:
    name: str
    joined_order: int


@dataclass
class Payout:
    week: int
    recipient: str
    amount: Decimal


@dataclass
class SusuGroup:
    weekly_contribution: Decimal
    members: List[Member] = field(default_factory=list)
    current_week: int = 1
    payments: Dict[int, Dict[str, Decimal]] = field(default_factory=dict)
    payout_history: List[Payout] = field(default_factory=list)
    _started: bool = False

    def __post_init__(self):
        self.weekly_contribution = money(self.weekly_contribution)
        if self.weekly_contribution <= 0:
            raise ValueError("Weekly contribution must be greater than zero.")

    def add_member(self, name: str) -> None:
        cleaned = name.strip()
        if not cleaned:
            raise ValueError("Member name or ID cannot be empty.")
        if any(m.name.casefold() == cleaned.casefold() for m in self.members):
            raise ValueError(f"Member '{cleaned}' already exists.")
        if self._started or self.current_week > 1:
            raise ValueError("Members cannot be added after the first week has started.")
        self.members.append(Member(cleaned, len(self.members) + 1))
        self.payments.setdefault(self.current_week, {})[cleaned] = Decimal("0.00")

    def _find_member(self, name: str) -> Member:
        cleaned = name.strip()
        for member in self.members:
            if member.name.casefold() == cleaned.casefold():
                return member
        raise ValueError(f"Unknown member: '{name}'.")

    def amount_paid(self, name: str, week: int | None = None) -> Decimal:
        member = self._find_member(name)
        selected_week = self.current_week if week is None else week
        return self.payments.get(selected_week, {}).get(member.name, Decimal("0.00"))

    def amount_owed(self, name: str, week: int | None = None) -> Decimal:
        return self.weekly_contribution - self.amount_paid(name, week)

    def record_contribution(self, name: str, amount) -> None:
        member = self._find_member(name)
        payment = money(amount)
        if payment <= 0:
            raise ValueError("Payment must be greater than zero.")
        paid = self.payments.setdefault(self.current_week, {}).get(
            member.name, Decimal("0.00")
        )
        owed = self.weekly_contribution - paid
        if payment > owed:
            raise ValueError(
                f"Payment exceeds amount owed. {member.name} owes {format_ghs(owed)}."
            )
        self.payments[self.current_week][member.name] = paid + payment
        self._started = True

    def close_week(self) -> str:
        if not self.members:
            raise ValueError("Add at least one member before closing a week.")

        outstanding = [
            (member.name, self.amount_owed(member.name))
            for member in self.members
            if self.amount_owed(member.name) > 0
        ]
        if outstanding:
            details = ", ".join(
                f"{name} owes {format_ghs(amount)}" for name, amount in outstanding
            )
            return f"Week {self.current_week} cannot close. {details}."

        recipient = self.members[(self.current_week - 1) % len(self.members)]
        pot = self.weekly_contribution * len(self.members)
        self.payout_history.append(Payout(self.current_week, recipient.name, pot))
        closed_week = self.current_week
        self.current_week += 1
        self.payments[self.current_week] = {
            member.name: Decimal("0.00") for member in self.members
        }
        self._started = False
        return (
            f"Week {closed_week} closed. {recipient.name} receives "
            f"{format_ghs(pot)}. Week {self.current_week} has started."
        )

    def report(self) -> str:
        lines = [
            "=== SUSU GROUP REPORT ===",
            f"Current week: {self.current_week}",
            f"Weekly contribution per member: {format_ghs(self.weekly_contribution)}",
            f"Members: {len(self.members)}",
            "",
            "Current-week payments:",
        ]
        if not self.members:
            lines.append("  No members registered.")
        for member in self.members:
            paid = self.amount_paid(member.name)
            owed = self.amount_owed(member.name)
            status = "PAID IN FULL" if owed == 0 else "OWES"
            lines.append(
                f"  {member.name}: paid {format_ghs(paid)}, "
                f"owes {format_ghs(owed)} [{status}]"
            )
        lines.append("")
        lines.append("Payout history:")
        if not self.payout_history:
            lines.append("  No payouts yet.")
        for payout in self.payout_history:
            lines.append(
                f"  Week {payout.week}: {payout.recipient} received "
                f"{format_ghs(payout.amount)}"
            )
        return "\n".join(lines)


def ask_amount(prompt: str) -> Decimal:
    return money(input(prompt).strip())


def main() -> None:
    print("Susu Group Tracker")
    while True:
        try:
            weekly = ask_amount("Fixed weekly contribution in GHS (e.g. 50.00): ")
            group = SusuGroup(weekly)
            break
        except ValueError as exc:
            print(f"Error: {exc}")

    print("Create your group. Add members in payout order.")
    while True:
        name = input("Member name/ID (or press Enter to finish): ").strip()
        if not name:
            break
        try:
            group.add_member(name)
            print(f"Added {name}.")
        except ValueError as exc:
            print(f"Error: {exc}")

    while True:
        print(
            "\n1. Add member\n2. Record contribution\n3. Close current week\n"
            "4. Show report\n5. Exit"
        )
        choice = input("Choose an option: ").strip()
        try:
            if choice == "1":
                group.add_member(input("Member name/ID: "))
                print("Member added.")
            elif choice == "2":
                name = input("Member name/ID: ")
                amount = ask_amount("Payment amount in GHS: ")
                group.record_contribution(name, amount)
                print("Contribution recorded.")
            elif choice == "3":
                print(group.close_week())
            elif choice == "4":
                print(group.report())
            elif choice == "5":
                print("Goodbye.")
                break
            else:
                print("Choose a number from 1 to 5.")
        except ValueError as exc:
            print(f"Error: {exc}")


if __name__ == "__main__":
    main()
