import marimo

__generated_with = "0.17.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # SIR Models

    The original SIR model was proposed in "Contribution to the Mathematical Theory of Epidemics" William Kermack and Anderson McKendrick, 1927. The population($N$) is divided into 3 pools: $S$, $I$, and $R$.

    \begin{align}
    S \rightarrow I \rightarrow R
    \end{align}

    At each timestep, individuals move between the 3 pools.
    """)
    return


@app.cell
def _():
    import numpy as np
    import pandas as pd
    import altair as alt
    return alt, np, pd

@app.cell
def __(mo):
    beta_slider = mo.ui.slider(
        start=0.1, stop=1.0, step=0.05, value=0.50, label="β (rate of infection)"
    )
    gamma_slider = mo.ui.slider(
        start=0.05, stop=0.5, step=0.05, value=0.20, label="γ (rate of recovery)"
    )
    timesteps_slider = mo.ui.slider(
        start=50, stop=300, step=10, value=137, label="Timesteps"
    )
    return beta_slider, gamma_slider, timesteps_slider


@app.cell
def __(beta_slider, gamma_slider, mo, timesteps_slider):
    mo.md(
        f"""
        ## Simulation Parameters

        {beta_slider}

        {gamma_slider}

        {timesteps_slider}
        """
    )
    return


@app.cell
def _(alt, np, pd):
    # SIR Model Parameters
    beta = beta_slider.value
    gamma = gamma_slider.value
    timesteps = timesteps_slider.value

    # Initial populations
    init_S = 7900000
    init_I = 10
    init_R = 0
    N = init_S + init_I + init_R

    # Initialize dataframe
    sim_data = pd.DataFrame({
        't': range(1, timesteps + 1),
        's': np.zeros(timesteps),
        'i': np.zeros(timesteps),
        'r': np.zeros(timesteps)
    })

    # Set initial conditions
    sim_data.loc[0, 's'] = init_S / N
    sim_data.loc[0, 'i'] = init_I / N
    sim_data.loc[0, 'r'] = init_R / N

    # Run simulation
    for ii in range(1, timesteps):
        s_prev = sim_data.loc[ii-1, 's']
        i_prev = sim_data.loc[ii-1, 'i']
        r_prev = sim_data.loc[ii-1, 'r']

        sim_data.loc[ii, 's'] = s_prev - beta * s_prev * i_prev
        sim_data.loc[ii, 'i'] = i_prev + beta * s_prev * i_prev - gamma * i_prev
        sim_data.loc[ii, 'r'] = r_prev + gamma * i_prev


    # Reshape data for Altair (long format)
    sim_long = pd.melt(
        sim_data,
        id_vars=['t'],
        value_vars=['s', 'i', 'r'],
        var_name='variable',
        value_name='value'
    )

    # Map variable names to full labels
    variable_labels = {
        's': 'Susceptible',
        'i': 'Infected',
        'r': 'Recovered'
    }
    sim_long['Population'] = sim_long['variable'].map(variable_labels)

    # Create Altair chart
    chart = alt.Chart(sim_long).mark_line(size=3).encode(
        x=alt.X('t:Q', title='Timestep'),
        y=alt.Y('value:Q',
                title='Population Proportion',
                axis=alt.Axis(
                    tickCount=5,
                    format='%'
                )),
        color=alt.Color('Population:N',
                       scale=alt.Scale(
                           domain=['Susceptible', 'Infected', 'Recovered'],
                           range=['#00BFC4', '#F8766D', '#7CAE00']
                       )),
        tooltip=[
            alt.Tooltip('t:Q', title='Timestep'),
            alt.Tooltip('Population:N'),
            alt.Tooltip('value:Q', title='Proportion', format='.2%')
        ]
    ).properties(
        width=700,
        height=400,
        title=f'SIR Simulation (β = {beta:.2f}, γ = {gamma:.2f})'
    ).interactive()

    chart
    return


if __name__ == "__main__":
    app.run()
