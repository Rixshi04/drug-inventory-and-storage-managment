class DistributionStreamlining:
    def __init__(self, inventory):
        self.inventory = inventory
        self.distribution_plan = []

    def create_distribution_plan(self, institutions):
        for institution in institutions:
            drug_id = institution['drug_id']
            needed_quantity = institution['needed_quantity']
            available_stock = self.inventory.inventory.get(drug_id, {}).get('stock', 0)
            if available_stock >= needed_quantity:
                self.distribution_plan.append({
                    'institution': institution['name'],
                    'drug_id': drug_id,
                    'quantity': needed_quantity
                })
                self.inventory.update_stock(drug_id, -needed_quantity)
            else:
                print(f"Not enough stock for {institution['name']}")

    def execute_distribution(self):
        for plan in self.distribution_plan:
            print(f"Delivering {plan['quantity']} units of drug ID {plan['drug_id']} to {plan['institution']}.")

# Example usage:
institutions = [
    {'name': 'Hospital A', 'drug_id': 101, 'needed_quantity': 30},
    {'name': 'Clinic B', 'drug_id': 102, 'needed_quantity': 20}
]
distribution = DistributionStreamlining(inventory)
distribution.create_distribution_plan(institutions)
distribution.execute_distribution()
