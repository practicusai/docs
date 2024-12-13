---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.4
  kernelspec:
    display_name: Practicus Core
    language: python
    name: practicus
---

## Introduction to Polars

Polars is a high-performance DataFrame library designed for efficient and fast data manipulation. Built in Rust and leveraging Apache Arrow, Polars provides a modern, user-friendly API for working with structured data. It offers several advantages over traditional libraries like Pandas and Dask:

### Why Use Polars?

#### Key Benefits:
1. **Speed**: Written in Rust and optimized for performance, Polars is significantly faster for many operations compared to Pandas.
2. **Memory Efficiency**: Polars uses Arrow memory structures, which are compact and designed for zero-copy interprocess communication.
3. **Parallelism**: Automatically leverages multiple CPU cores for computations.
4. **Lazy Evaluation**: Allows defining a series of operations that are only computed when needed, improving efficiency for complex workflows.
5. **Interoperability**: Easy to switch between Polars and Pandas, allowing incremental adoption.

---

#### Example: Basic Polars Operations with `diamond.csv`

In this notebook, we will:
1. Load the `diamonds.csv` dataset using Polars.
2. Explore the dataset with basic info commands.
3. Perform simple data manipulations.
4. Showcase interoperation between Polars and Pandas.

```python
# Import Polars
import polars as pl

# Read the dataset using Polars
df = pl.read_csv("../../diamond.csv")

# Basic exploration
print("Shape of the dataset:", df.shape)
print("First few rows of the dataset:")
print(df.head())
```

```python
# Summary statistics
print("Summary statistics:")
print(df.describe())
```

```python
# Filter rows where carat is greater than 2
filtered_df = df.filter(pl.col("Carat Weight") > 2)
print("Filtered rows where Carat Weight > 2:")
print(filtered_df)
```

```python
# Convert to Pandas DataFrame
pandas_df = df.to_pandas()
print("Converted to Pandas DataFrame:")
display(pandas_df.head())
```

```python
# Convert back to Polars DataFrame
polars_df = pl.from_pandas(pandas_df)
print("Converted back to Polars DataFrame:")
print(polars_df.head())
```

```python

```


---

**Previous**: [Spark Custom Config](spark-custom-config.md) | **Next**: [Deploy Workflow](deploy-workflow.md)