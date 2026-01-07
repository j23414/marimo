import marimo

__generated_with = "0.17.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    import pandas as pd
    import altair as alt
    import io
    return alt, pd


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Norovirus Data Explorer

    Exploring norovirus metadata from Nextstrain curated metadata.tsv.zst file
    """)
    return


@app.cell
def _(pd):
    url = "https://data.nextstrain.org/files/workflows/norovirus/metadata.tsv.zst"

    print("Fetching data from Nextstrain...")

    try:
        df = pd.read_csv(url, sep='\t', compression='zstd', dtype="str")
        print(f"Loaded {len(df):,} records successfully!")
    except Exception as e:
        print(f"Note: {e}")
        print("Could not load data. Using sample data for demo.")
        # Create sample data structure for demo
        df = pd.DataFrame({
            'strain': ['demo_sample1', 'demo_sample2'],
            'date': ['2020-01-01', '2021-01-01'],
            'country': ['USA', 'UK'],
            'VP1_group': ['GII.4', 'GII.2']
        })

    df.head()
    return (df,)


@app.cell
def _(df, mo):
    mo.md(f"""
    ## Dataset Overview

    - **Total records:** {len(df):,}
    - **Columns:** {len(df.columns)}
    - **Date range:** {df['date'].min() if 'date' in df.columns else 'N/A'} to {df[~df['date'].str.startswith('XXXX', na=False)]['date'].max() if 'date' in df.columns else 'N/A'}
    """)
    return


@app.cell
def _():
    # Show available columns
    #print("Available columns:")
    #df.columns.tolist()
    return


@app.cell
def _(mo):
    stack_col = mo.ui.dropdown(
        options=["VP1_group", "VP1_type", "VP1_variant", "RdRp_group", "RdRp_type", "RdRp_variant","region", "country", "division", "location", "host_type"],
        value="VP1_type",
        label="Stack by:"
    )
    stack_col
    return (stack_col,)


@app.cell
def _(df, pd, stack_col):
    stack = stack_col.value

    # Extract year from date column
    df_with_year = df.copy()
    df_with_year['year'] = pd.to_datetime(df_with_year['date'], errors='coerce').dt.year

    # Remove rows with invalid years
    df_with_year = df_with_year.dropna(subset=['year'])
    df_with_year['year'] = df_with_year['year'].astype(int)

    # Count records per year and VP1 Group
    #records_per_year = df_with_year.groupby(['year', 'group']).size().reset_index(name='count')
    records_per_year = (
        df_with_year
          .groupby(['year', stack])
          .size()
          .reset_index(name='count')
    )
    records_per_year
    return records_per_year, stack


@app.cell
def _(alt, records_per_year, stack):
    # Records per year chart
    year_chart = alt.Chart(records_per_year).mark_bar().encode(
        x=alt.X('year:O', title='Year'),
        y=alt.Y('count:Q', title='Number of Records'),
        #color=alt.Color('VP1_type:N', title='VP1 group'),
        color=alt.Color(f"{stack}:N", title=stack),
        tooltip=['year:O', 'count:Q']
    ).properties(
        width=700,
        height=400,
        title='Norovirus Records per Year'
    ).interactive()

    year_chart
    return


if __name__ == "__main__":
    app.run()
