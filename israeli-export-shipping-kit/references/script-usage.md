# Helper Script Input Fields

`scripts/generate_invoice.py` reads a JSON order. Start from `scripts/sample_order.json`.

## Required

Required top-level fields: `invoice_number`, `invoice_date`, `incoterm`, `seller`, `buyer`, `items`. `seller` needs `name_en`, `address` and `vat_id` (add `name_he` for the Hebrew column); `buyer` needs `name_en`, `address` and `country`. Each entry in `items` needs `description_en`, `quantity` and `unit_price`, plus `hs_code`, `description_he`, `gross_kg` and `net_kg` if you want them on the invoice and packing list. Optional: `currency` (defaults to USD), `named_place` for the Incoterm, `freight` and `insurance`. The script validates these up front and names anything missing.

## Optional fields worth setting

Two more optional fields worth setting. `country_of_origin` defaults to ISRAEL but is
honoured if you set it, which matters the moment you re-export goods made somewhere else:
printing ISRAEL on a customs document for non-Israeli goods is a false origin statement,
not a formatting choice. `reason_for_export` (sale, sample, repair, return) is printed when
present and is what a customs officer looks for on a non-sale shipment.

Origin-declaration fields (`origin_declaration`, `origin_place`, `origin_postcode`, `approved_exporter_number`) and `buyer.eori` are described in SKILL.md Step 7.
