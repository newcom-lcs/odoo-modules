# Purchase Split PO

This Odoo 16 module allows users to create a new Purchase Order (PO) from a line inside an existing PO.

## Features

- Create a new Purchase Order from an existing line
- Select a supplier for the new PO through a wizard
- Supports Make to Order (MTO) + Make to Stock (MTS) logistics
- Maintains links to the original Sales Order (SO)
- Properly handles stock moves and reservations

## Usage

1. Go to an existing Purchase Order in draft or sent state
2. Find the line you want to move to a new PO
3. Click the "Create New PO" button (fork icon) next to the product
4. In the wizard:
   - Select a supplier
   - Adjust the quantity if needed
   - Change the expected date if needed
5. Click "Create New PO"
6. The system will create a new PO with the selected line

## Technical Information

The module handles both MTO and MTS scenarios:

- For MTO: The procurement group is maintained to ensure proper linking to the original SO
- For MTS: Stock moves are properly adjusted to follow normal replenishment rules
- The split operation properly divides stock moves and reservations to avoid conflicts

## Requirements

- Odoo 16
- purchase_stock module 