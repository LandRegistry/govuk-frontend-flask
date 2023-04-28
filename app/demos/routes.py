import json
import os
from typing import Union

from flask import flash, redirect, render_template, url_for
from werkzeug import Response
from werkzeug.exceptions import NotFound

from app.demos import bp
from app.demos.forms import BankDetailsForm, ConditionalRevealForm, CreateAccountForm, KitchenSinkForm


@bp.route("/components", methods=["GET"])
def components() -> str:
    components = os.listdir("govuk_components")
    components.sort()

    return render_template("components.html", components=components)


@bp.route("/components/<string:component>", methods=["GET"])
def component(component) -> str:
    try:
        with open("govuk_components/{}/fixtures.json".format(component)) as json_file:
            fixtures = json.load(json_file)
    except FileNotFoundError:
        raise NotFound

    return render_template("component.html", fixtures=fixtures)


@bp.route("/forms", methods=["GET"])
def forms() -> str:
    return render_template("forms.html")


@bp.route("/forms/bank-details", methods=["GET", "POST"])
def bank_details() -> Union[str, Response]:
    form = BankDetailsForm()
    if form.validate_on_submit():
        flash("Demo form successfully submitted", "success")
        return redirect(url_for("demos.forms"))
    return render_template("bank_details.html", form=form)


@bp.route("/forms/create-account", methods=["GET", "POST"])
def create_account() -> Union[str, Response]:
    form = CreateAccountForm()
    if form.validate_on_submit():
        flash("Demo form successfully submitted", "success")
        return redirect(url_for("demos.forms"))
    return render_template("create_account.html", form=form)


@bp.route("/forms/kitchen-sink", methods=["GET", "POST"])
def kitchen_sink() -> Union[str, Response]:
    form = KitchenSinkForm()
    if form.validate_on_submit():
        flash("Demo form successfully submitted", "success")
        return redirect(url_for("demos.forms"))
    return render_template("kitchen_sink.html", form=form)


@bp.route("/forms/conditional-reveal", methods=["GET", "POST"])
def conditional_reveal() -> Union[str, Response]:
    form = ConditionalRevealForm()
    if form.validate_on_submit():
        flash("Demo form successfully submitted", "success")
        return redirect(url_for("demos.forms"))
    return render_template("conditional_reveal.html", form=form)
