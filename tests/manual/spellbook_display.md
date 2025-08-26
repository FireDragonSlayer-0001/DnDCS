# Spellbook Display Reproduction Steps

1. Start the UI server:
   ```
   uvicorn dndcs.ui.server:app --port 8000
   ```
2. Open `http://localhost:8000` in a browser.
3. Click **Open** and load `tests/data/wizard_l17.json`.
4. The spellbook item from inventory is detected and the spells listed under the *Spells* tab appear immediately.
5. Toggle a prepared spell checkbox or add a new known spell and observe that the **Raw** panel updates `current.items` to reflect the changes.
