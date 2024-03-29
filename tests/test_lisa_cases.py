import matplotlib.pyplot as plt
import numpy as np
import pytest

from slipper.example_datasets.ar_data import generate_ar_timeseries as gen
from slipper.example_datasets.lisa_data import (
    lisa_noise_periodogram,
    lisa_wd_strain,
)
from slipper.fourier_methods import get_periodogram
from slipper.plotting.plot_spline_model_and_data import (
    plot_spline_model_and_data,
)
from slipper.sample import LogPsplineSampler
from slipper.sample import LogPsplineSamplerPara as lpp
from slipper.splines.knot_locator import KnotLocatorType

from .conftest import mkdir


def __plot_res(pdgrm, res, title, x=None):
    if x is not None:
        x = x[1:]
    fig = plot_spline_model_and_data(
        data=pdgrm,
        model_quants=res.psd_quantiles,
        knots=res.knots,
        add_legend=False,
        logged_axes=["x", "y"],
        hide_axes=False,
        x=x,
    )
    fig.suptitle(title)
    ax = fig.axes[0]
    ax.set_xlabel("Frequency")
    ax.set_ylabel("PSD")
    plt.tight_layout()
    return fig


# @pytest.mark.skip("Fails due to -inf qunatiles")
def test_fit_lisa_noise_linear_knots(tmpdir):
    np.random.seed(42)
    pdgrm = lisa_noise_periodogram()

    # Data truncation:
    fs = 1 / 0.75
    f = np.linspace(0, fs / 2, len(pdgrm))
    pdgrm = pdgrm[(f >= 1e-4) & (f <= 0.1)]

    outdir = mkdir(f"{tmpdir}/lisa/noise/linear_knots")
    res = LogPsplineSampler.fit(
        data=pdgrm,
        outdir=outdir,
        sampler_kwargs=dict(Ntotal=100, n_checkpoint_plts=2, burnin=10),
        spline_kwargs=dict(
            k=30,
            knot_locator_type=KnotLocatorType.linearly_spaced,
        ),
    )
    fig = __plot_res(pdgrm, res, "LISA noise", x=f[(f >= 1e-4) & (f <= 0.1)])
    fig.savefig(f"{outdir}/fit.png")


def test_fit_lisa_noise_binned_knots(tmpdir):
    np.random.seed(42)
    pdgrm = lisa_noise_periodogram()
    # keep every 5th point to speed up analysis for testing
    fs = 1 / 0.75
    f = np.linspace(0, fs / 2, len(pdgrm))
    pdgrm = pdgrm[(f >= 1e-4) & (f <= 0.1)]
    outdir = mkdir(f"{tmpdir}/lisa/noise/binned_knots")
    res = LogPsplineSampler.fit(
        data=pdgrm,
        outdir=outdir,
        sampler_kwargs=dict(
            Ntotal=100, n_checkpoint_plts=2, burnin=10, thin=1
        ),
        spline_kwargs=dict(
            k=30,
            knot_locator_type=KnotLocatorType.binned_knots,
            data_bin_edges=[1e-3, 1e-2],
            data_bin_weights=[0.1, 0.1, 0.8],
            log_data=True,
            n_grid_points=500,
        ),
    )
    fig = __plot_res(pdgrm, res, "LISA noise", x=f[(f >= 1e-4) & (f <= 0.1)])
    fig.savefig(f"{outdir}/fit.png")


def test_fit_list_wd_background(tmpdir):
    np.random.seed(42)
    timeseries = lisa_wd_strain()[0:1000]
    pdgrm = get_periodogram(timeseries=timeseries)

    outdir = mkdir(f"{tmpdir}/lisa/wdb/linear_knots")
    res = LogPsplineSampler.fit(
        data=pdgrm,
        outdir=outdir,
        sampler_kwargs=dict(
            Ntotal=100, n_checkpoint_plts=2, burnin=10, thin=1
        ),
        spline_kwargs=dict(
            k=30,
            knot_locator_type=KnotLocatorType.linearly_spaced,
        ),
    )
    fig = __plot_res(pdgrm, res, "White dwarf background")
    fig.savefig(f"{outdir}/fit.png")


def test_ar_param(tmpdir):
    np.random.seed(42)
    outdir = mkdir(f"{tmpdir}/lisa/noise/linear_knots/parametric")
    series = gen(order=5)
    # series = np.loadtxt(f"{outdir}/x-series.txt")#LISA time series
    # fs=1/0.75 #for LISA PSD
    res = lpp.fit(
        data=series,
        outdir=outdir,
        sampler_kwargs=dict(Ntotal=100, n_checkpoint_plts=2, burnin=10),
        spline_kwargs=dict(
            k=60,
            knot_locator_type=KnotLocatorType.linearly_spaced,
        ),
    )
    pdgrm = get_periodogram(timeseries=series)  # ,fs=fs)#for LISA
    # f=np.linspace(start=0,stop=1.333/2,num=len(pdgrm))#for truncation
    # pdgrm=pdgrm[(f >= 1e-4) & (f <= 0.1)]
    fig = __plot_res(
        pdgrm, res, "AR"
    )  # , x=f[(f >= 1e-4) & (f <= 0.1)])#for LISA
    fig.savefig(f"{outdir}/fitar.png")
