from dataclasses import dataclass

@dataclass
class CustomerOrder(object):
  order_id: int
  customer_id: str
  item_namE: str

order = CustomerOrder(1, '001', 'Guitar')
print(order)
