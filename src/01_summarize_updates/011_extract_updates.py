'''
Inputs: Deck, structured GSPBM data
Output: update-indexed implicated (s)BSP w/ justifications JSON.

This script extracts proposed updates to the GSBPM from a
reference document, listing for each (s)BSP that are
affected by the update. (s)BSPs are identified either by
being explicitly stated, or deduced by the LLM. Each
implicated (s)BSP includes a justification for association
with the update.


 - (s)BSP: a phase or sub-phase from the GSBPM.
'''
