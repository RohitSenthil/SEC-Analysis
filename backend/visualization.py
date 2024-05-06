import base64
from io import BytesIO

import matplotlib.pyplot as plt
import numpy as np

impact_map = {
    "negligable": 0,
    "low": 1,
    "moderate": 2,
    "significant": 3,
    "catastrophic": 4,
}
likelihood_map = {
    "improbable": 0,
    "remote": 1,
    "occasional": 2,
    "probable": 3,
    "frequent": 4,
}

cmap = [
    ["#74b062", "#74b062", "#74b062", "#a0c163", "#a0c163"],
    ["#74b062", "#a0c163", "#a0c163", "#f5db65", "#f5db65"],
    ["#74b062", "#a0c163", "#f5db65", "#f5db65", "#e49a51"],
    ["#a0c163", "#f5db65", "#f5db65", "#d84432", "#d84432"],
    ["#a0c163", "#f5db65", "#e49a51", "#d84432", "#d84432"],
]
header_colors = plt.cm.BuPu(np.full(5, 0.1))


def get_table(ticker: str, risk_factors: list[dict[str, str]]) -> bytes:
    table_arr = [["" for _ in range(5)] for _ in range(5)]
    for risk_factor in risk_factors:
        impact = impact_map[risk_factor["impact"]]
        likelihood = likelihood_map[risk_factor["likelihood"]]
        table_arr[impact][likelihood] = (
            table_arr[impact][likelihood] + risk_factor["risk"] + "\n"
        )
    plt.figure(
        linewidth=2,
        tight_layout={"pad": 1},
        figsize=(15, 5),
    )
    ax = plt.gca()
    risk_table = plt.table(
        cellText=table_arr,
        rowLabels=list(impact_map.keys()),
        colLabels=list(likelihood_map.keys()),
        rowColours=header_colors,
        colColours=header_colors,
        cellColours=cmap,
        loc="center",
    )
    risk_table.auto_set_column_width(range(5))
    risk_table.scale(1, 5)
    plt.suptitle(f"Risk Heat Map for {ticker}")
    ax.get_yaxis().set_visible(False)
    ax.get_xaxis().set_visible(False)
    ax.axis("off")
    ax.axis("tight")
    plt.box(on=None)
    fig = plt.gcf()
    # fig.canvas.draw()
    fig.tight_layout()
    plt.tight_layout()
    plt.draw()
    buf = BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    encoded_string = base64.b64encode(buf.getbuffer())
    return encoded_string
