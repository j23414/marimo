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
def _(df):
    # Show available columns
    print("Available columns:")
    df.columns.tolist()
    return


@app.cell
def _(df, pd):
    # Extract year from date column
    df_with_year = df.copy()
    df_with_year['year'] = pd.to_datetime(df_with_year['date'], errors='coerce').dt.year

    # Remove rows with invalid years
    df_with_year = df_with_year.dropna(subset=['year'])
    df_with_year['year'] = df_with_year['year'].astype(int)

    # Count records per year
    records_per_year = df_with_year.groupby('year').size().reset_index(name='count')
    records_per_year
    return df_with_year, records_per_year


@app.cell
def _(alt, records_per_year):
    # Records per year chart
    year_chart = alt.Chart(records_per_year).mark_bar().encode(
        x=alt.X('year:O', title='Year'),
        y=alt.Y('count:Q', title='Number of Records'),
        tooltip=['year:O', 'count:Q']
    ).properties(
        width=700,
        height=400,
        title='Norovirus Records per Year'
    ).interactive()

    year_chart
    return


@app.cell
def _(df_with_year):
    # Check if VP1_group exists and count by year and group
    if 'VP1_group' in df_with_year.columns:
        records_by_group = df_with_year.groupby(['year', 'VP1_group']).size().reset_index(name='count')
        # Filter to top groups for cleaner visualization
        top_groups = records_by_group.groupby('VP1_group')['count'].sum().nlargest(10).index
        records_by_group = records_by_group[records_by_group['VP1_group'].isin(top_groups)]
        records_by_group
    else:
        print("VP1_group column not found. Available columns:")
        print(df_with_year.columns.tolist())
        records_by_group = None

    print("hello")
    return (records_by_group,)


@app.cell
def _(alt, records_by_group):
    # Stacked bar chart by VP1_group if available
    if records_by_group is not None:
        group_chart = alt.Chart(records_by_group).mark_bar().encode(
            x=alt.X('year:O', title='Year'),
            y=alt.Y('count:Q', title='Number of Records'),
            color=alt.Color('VP1_group:N', title='VP1 Group', scale=alt.Scale(scheme='category20')),
            tooltip=['year:O', 'VP1_group:N', 'count:Q']
        ).properties(
            width=700,
            height=400,
            title='Norovirus Records per Year by VP1 Group (Top 10 Groups)'
        ).interactive()

        group_chart
    else:
        print("Cannot create VP1_group chart - column not found")
    return


@app.cell
def _(df_with_year):
    # Geographic distribution if country column exists
    if 'country' in df_with_year.columns:
        country_counts = df_with_year['country'].value_counts().reset_index()
        country_counts.columns = ['country', 'count']
        country_counts.head(20)
    else:
        country_counts = None
    return (country_counts,)


@app.cell
def _(alt, country_counts):
    # Top countries bar chart
    if country_counts is not None:
        country_chart = alt.Chart(country_counts.head(20)).mark_bar().encode(
            x=alt.X('count:Q', title='Number of Records'),
            y=alt.Y('country:N', title='Country', sort='-x'),
            tooltip=['country:N', 'count:Q']
        ).properties(
            width=700,
            height=500,
            title='Top 20 Countries by Number of Records'
        ).interactive()

        country_chart
    else:
        print("Cannot create country chart - column not found")
    return


if __name__ == "__main__":
    app.run()
