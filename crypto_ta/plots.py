#    This script is part of crypto_ta
#    Copyright (C) 2021 dokato

import mplfinance as mpf
import matplotlib.pyplot as plt

__all__ = ["mfp_plot", "plot_candle", "plot_renko", "plot_basic",
           "plot_ta_feature"]

def mfp_plot(df, moving_averages = (3,6,9), volume = True, lastn = None,
             type='candle', title=None):
    if not lastn is None:
        df = df[-lastn:]
    fig, axes = mpf.plot(df, type=type, mav=moving_averages, volume=volume,
                         returnfig=True)
    # Configure chart legend and title
    axes[0].legend([f"MA {i}" for i in moving_averages])
    if title:
        axes[0].set_title(title)
    fig.show()

def plot_candle(df, moving_averages = (3,6,9),
                volume = True, lastn = None):
    mfp_plot(df, moving_averages=moving_averages, volume=volume,
             lastn=lastn, type='candle')

def plot_renko(df, moving_averages = (3,6,9),
                volume = True, lastn = None):
    mfp_plot(df, moving_averages=moving_averages, volume=volume,
             lastn=lastn, type='renko')

def plot_basic(df, moving_averages = (3,6,9),
                volume = True, lastn = None):
    mfp_plot(df, moving_averages=moving_averages, volume=volume,
             lastn=lastn, type='ohlc')

def plot_ta_feature(df, feature_name, style='r-', show=False, **kwargs):
    plt.plot(df.index, df[feature_name], style, **kwargs)
    plt.ylabel(feature_name)
    locs, labels = plt.xticks()
    plt.setp(labels, rotation=45)
    if show:
        plt.show()