///<reference path="//Microsoft.WinJS.1.0/js/base.js" />
///<reference path="//Microsoft.WinJS.1.0/js/ui.js" />
(function () {
    "use strict";

    Athena.Widget.EditRemarknameFlyout = WinJS.Class.derive(Athena.UI.Flyout, function () {
        Athena.UI.Flyout.apply(this, arguments);
        this.render();
    }, {
        render: function () {
            var that = this;
            var flyoutAnchor = that.anchor;
            var uin = parseInt(that.uin, 10);
            var flyout = that.flyout;
            var flyoutMain = that.flyoutMain;

            // 渲染
            var remarkNameField = {
                id: "athena-edit-remarknameui-remarkname",
                maxlength: 8
            };
            that._titleTemplate.render({ text: "修改备注" }, flyoutMain);
            that._textfieldTemplate.render({ placeholder: "", value: that.text || "" }, flyoutMain).done(function (root) {
                var el = root.lastElementChild;
                el.setAttribute("id", remarkNameField.id);
                el.setAttribute("maxlength", remarkNameField.maxlength);
            });
            that._actionsTemplate.render(null, flyoutMain);
            WinJS.Utilities.query(".athena-ui-flyout-action-confirm", flyoutMain).listen("click",
            function () {
                var newRemarkName = document.getElementById(remarkNameField.id).value;
                var contactCache = IMERT.ServiceHub.getContactCache();
                contactCache.onsetuserremarkresult = function (evt) {
                    var ret;
                    flyout.hide();
                    ret = Athena.Utilities.toJson(evt.target || "");
                    if ((uin + "") === ret.uin) {
                        if (!ret || !ret.result) {
                            Athena.Utilities.showToast("修改备注失败");
                        }
                    }
                    contactCache.onsetuserremarkresult = null;
                };
                contactCache.setUserRemark(uin, newRemarkName);
            }, false);
            WinJS.Utilities.query(".athena-ui-flyout-action-cancel", flyoutMain).listen("click",
            function () {
                flyout.hide();
            }, false);
            flyout.show(flyoutAnchor);
        }
    });

    Athena.Widget.EditRemarknameFlyout.create = function (uin, text, anchor, sticky) {
        var flyoutOption = sticky ? { _sticky: true } : null;
        var opt = {
            uin: uin,
            text: text,
            anchor: anchor
        };
        if (flyoutOption) {
            opt.flyoutOption = flyoutOption;
        }
        return new Athena.Widget.EditRemarknameFlyout(null, opt);
    };
})();