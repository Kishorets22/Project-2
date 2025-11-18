### Project-2
# Local Food Wastage Management System
Food wastage is a significant issue, with many households and restaurants discarding surplus food while numerous people struggle with food insecurity. This project aims to develop a Local Food Wastage Management System, where: Restaurants and individuals can list surplus food. NGOs or individuals in need can claim the food. SQL stores available food details and locations. A Streamlit app enables interaction, filtering, CRUD operation and visualization
# Project details
Objective: build an end-to-end Local Food Wastage Management System to connect donors (restaurants/individuals) with receivers (NGOs/individuals) and reduce food waste.
Data sources: the app uses four core tables / CSV files in the workspace:
providers_data.csv (providers listings)
receivers_data.csv (receiver registrations)
food_listings_data.csv (food items, quantities, expiry, location)
claims_data.csv (claims made by receivers)
# Key features:
Listing and searching available food by location, type, expiry and meal type.
Claiming workflow: receivers can claim listed items; claims are tracked and updated.
CRUD operations for all entities (providers, receivers, food listings, claims) with changes persisted to CSV and synchronized to a MySQL database.
Analytical views: aggregate summaries, top providers/items, expiry alerts and time-series of claims.
Architecture / tech stack:
Front-end: Streamlit pages (UI for filters, forms, and dashboards)
Data layer: CSV files as local sources; optional MySQL for persistent storage and sync
Libraries: Python, pandas, mysql-connector-python, Streamlit
