from flask import flash, redirect, render_template, url_for

from app.demos import bp
from app.demos.forms import BankDetailsForm, ConditionalRevealForm, CreateAccountForm, KitchenSinkForm


@bp.route("/forms/bank-details", methods=["GET", "POST"])
def bank_details():
    form = BankDetailsForm()
    if form.validate_on_submit():
        flash("Form successfully submitted", "success")
        return redirect(url_for("main.index"))
    return render_template("bank_details.html", form=form)


@bp.route("/forms/create-account", methods=["GET", "POST"])
def create_account():
    form = CreateAccountForm()
    if form.validate_on_submit():
        flash("Form successfully submitted", "success")
        return redirect(url_for("main.index"))
    return render_template("create_account.html", form=form)


@bp.route("/forms/kitchen-sink", methods=["GET", "POST"])
def kitchen_sink():
    form = KitchenSinkForm()
    if form.validate_on_submit():
        flash("Form successfully submitted", "success")
        return redirect(url_for("main.index"))
    return render_template("kitchen_sink.html", form=form)


@bp.route("/forms/conditional-reveal", methods=["GET", "POST"])
def conditional_reveal():
    form = ConditionalRevealForm()
    if form.validate_on_submit():
        flash("Form successfully submitted", "success")
        return redirect(url_for("main.index"))
    return render_template("conditional_reveal.html", form=form)
