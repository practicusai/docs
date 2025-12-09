---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.17.3
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

# Practicus AI Pattern Mining Documentation

This example documents a set of **built-in pattern mining snippets** that can be used in the platform:

- `apriori_association_rules`
- `sequence_markov_transitions`
- `carma_windowed_association_rules`
- `fpgrowth_association_rules`
- `sequence_mining_contiguous`




## 1. `apriori_association_rules`

**Purpose:**

Finds **association rules** (e.g. `Milk -> Bread`) from transactional data using the Apriori algorithm. This is a classic *market basket analysis* / **birliktelik analizi** method.

**Expected input DataFrame columns:**

- `transaction_id_col`: column containing the **transaction or basket ID** (e.g., `OrderID`, `BasketId`).
- `item_col`: column containing the **item / product identifier** (e.g., `ProductName`, `ItemCode`).

Each row represents one `(transaction, item)` pair.

**Parameters:**

- `df`: the input DataFrame.
- `transaction_id_col` (str): name of the transaction ID column.
- `item_col` (str): name of the item column.
- `min_support` (float, default 0.05): minimum fraction of transactions that must contain an itemset.
- `min_confidence` (float, default 0.6): minimum confidence for a rule `A -> B`.
- `min_lift` (float or None, default None): if set, rules with lift below this threshold are removed.
- `max_rules` (int or None, default 100): maximum number of rules to return.

**Output:**

A new DataFrame with one row per rule, typically with columns like:

- `antecedent`: left-hand side itemset as a string (e.g., `"Milk"`, `"Milk, Bread"`).
- `consequent`: right-hand side itemset as a string.
- `support`: support of the full rule (fraction of all transactions).
- `confidence`: confidence of the rule.
- `lift`: lift of the rule.

The platform can store this output as a new worksheet, e.g. `Apriori_Rules_<original_table>`.



## 2. `carma_windowed_association_rules`

**Purpose:**

Implements a **CARMA-style incremental association mining** by running Apriori on a **sliding window of the most recent transactions**. This approximates streaming / real-time association rule mining.

**Expected input DataFrame columns:**

- `transaction_id_col`: transaction or basket ID.
- `item_col`: item / product identifier.
- `timestamp_col` (optional): timestamp or order column used to determine which transactions are the most recent.

**Parameters:**

- `df`: the input DataFrame.
- `transaction_id_col` (str): name of the transaction ID column.
- `item_col` (str): name of the item column.
- `timestamp_col` (str or None, default None): name of the timestamp column. If `None`, the existing row order is used.
- `window_size_transactions` (int, default 10000): number of **most recent distinct transactions** to include in the analysis.
- `min_support` (float, default 0.05): minimum support within the window.
- `min_confidence` (float, default 0.6): minimum confidence.
- `min_lift` (float or None, default None): optional minimum lift.
- `max_rules` (int or None, default 100): limit on number of rules returned.

**Output:**

Same shape as `apriori_association_rules`: a table of rules with antecedent, consequent, support, confidence and lift. The difference is that all metrics are computed **only on the most recent window** of transactions.



## 3. `sequence_mining_contiguous`

**Purpose:**

Performs **Sequence mining** by finding **frequent contiguous subsequences** of events within ordered sequences.

Examples:
- `ViewProduct -> AddToCart -> Purchase`
- `Login -> Search -> Logout`

This satisfies the "Sequence" requirement for **ardışıklık tespiti**.

**Expected input DataFrame columns:**

- `sequence_id_col`: identifier of a sequence (e.g., `SessionID`, `CustomerID`, `CaseId`).
- `event_col`: event or action name at each step (e.g., `"View"`, `"AddToCart"`, `"Purchase"`).
- `order_by_col` (optional): column used to sort events inside each sequence (e.g., a timestamp or step index).

Each row represents one event in a sequence.

**Parameters:**

- `df`: the input DataFrame.
- `sequence_id_col` (str): name of the sequence ID column.
- `event_col` (str): name of the event/action column.
- `order_by_col` (str or None, default None): name of the column used to sort events.
- `min_support` (float, default 0.02): minimum fraction of sequences that must contain a pattern.
- `max_pattern_length` (int, default 5): maximum length of a pattern (e.g., 3 for `A -> B -> C`).
- `top_k` (int or None, default 100): maximum number of patterns to return.

**Output:**

A DataFrame where each row is a discovered pattern, with columns such as:

- `sequence`: the pattern as a string (e.g., `"ViewProduct -> AddToCart -> Purchase"`).
- `support`: number of sequences in which this pattern appears.
- `support_fraction`: support divided by total number of sequences.
- `length`: number of events in the pattern.



## 4. `fpgrowth_association_rules`

**Purpose:**

Performs association rule mining using the **FP-Growth** algorithm instead of Apriori. This demonstrates support for **multiple birliktelik analizi algorithms** and can be more efficient on large datasets.

**Expected input DataFrame columns:**

- `transaction_id_col`: transaction or basket ID.
- `item_col`: item / product identifier.

**Parameters:**

- `df`: the input DataFrame.
- `transaction_id_col` (str): name of the transaction ID column.
- `item_col` (str): name of the item column.
- `min_support` (float, default 0.05): minimum support threshold for frequent itemsets.
- `min_confidence` (float, default 0.6): minimum confidence for rules.
- `min_lift` (float or None, default None): optional minimum lift.
- `max_rules` (int or None, default 100): maximum number of rules to return.

**Output:**

Same structure as the Apriori-based snippet: a rule table with `antecedent`, `consequent`, `support`, `confidence` and `lift`.



## 5. `sequence_markov_transitions`

**Purpose:**

Computes **first-order Markov transition probabilities** between events in sequences. This focuses on **pairwise transitions** rather than longer patterns.

Example output:
- `ViewProduct -> AddToCart` with probability 0.4
- `AddToCart -> Purchase` with probability 0.7

This is another way to perform **ardışıklık analizi**.

**Expected input DataFrame columns:**

- `sequence_id_col`: identifier of a sequence (e.g., `SessionID`, `CustomerID`).
- `event_col`: event or action at each step.
- `order_by_col` (optional): column used to sort events inside each sequence.

**Parameters:**

- `df`: the input DataFrame.
- `sequence_id_col` (str): name of the sequence ID column.
- `event_col` (str): name of the event column.
- `order_by_col` (str or None, default None): name of the ordering column.
- `min_transition_count` (int, default 1): minimum number of occurrences of a transition to be included.
- `min_transition_probability` (float, default 0.0): minimum `P(target | source)` to be included.

**Output:**

A DataFrame with one row per transition, typically with columns:

- `source_event`: previous event (e.g., `"ViewProduct"`).
- `target_event`: next event (e.g., `"AddToCart"`).
- `count`: number of times this transition appears.
- `probability`: estimated probability `P(target_event | source_event)`.



## 6. Example Usage With a Simple CSV

All of these snippets can be demonstrated on a small CSV file with columns:

- `transaction_id`: transaction / basket identifier.
- `item`: product name.
- `sequence_id`: session or journey identifier.
- `event`: action taken (view, add to cart, purchase, etc.).
- `timestamp`: event time, used to order events.

Example:

```text
transaction_id,item,sequence_id,event,timestamp
T1,Milk,S1,ViewProduct,2025-01-01T09:00:00
T1,Bread,S1,AddToCart,2025-01-01T09:01:00
T1,Bread,S1,Purchase,2025-01-01T09:02:00
T2,Bread,S2,ViewProduct,2025-01-01T09:03:00
T2,Cheese,S2,AddToCart,2025-01-01T09:04:00
T2,Cheese,S2,Purchase,2025-01-01T09:05:00
T3,Cheese,S3,ViewProduct,2025-01-01T09:06:00
T3,Apples,S3,AddToCart,2025-01-01T09:07:00
T3,Apples,S3,Purchase,2025-01-01T09:08:00
T4,Apples,S4,ViewProduct,2025-01-01T09:09:00
T4,Oranges,S4,AddToCart,2025-01-01T09:10:00
```

With this CSV loaded into a DataFrame `df`, typical parameter mappings are:

### apriori_association_rules
  - `transaction_id_col = "transaction_id"`
  - `item_col = "item"`

### carma_windowed_association_rules
  - `transaction_id_col = "transaction_id"`
  - `item_col = "item"`
  - `timestamp_col = "timestamp"`

### fpgrowth_association_rules
  - `transaction_id_col = "transaction_id"`
  - `item_col = "item"`

###  sequence_mining_contiguous
  - `sequence_id_col = "sequence_id"`
  - `event_col = "event"`
  - `order_by_col = "timestamp"`

### sequence_markov_transitions
  - `sequence_id_col = "sequence_id"`
  - `event_col = "event"`
  - `order_by_col = "timestamp"`

The platform can expose these parameters in the UI and run the corresponding snippet on the selected table.



---

**Previous**: [AutoML](../AutoML.md) | **Next**: [Examples > Bank Marketing > Bank Marketing](../examples/bank-marketing/bank-marketing.md)
