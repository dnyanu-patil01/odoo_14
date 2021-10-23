odoo.define('kanha_census.partner_portal_form', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var Dialog = require('web.Dialog');

publicWidget.registry.portalPartnerDetails = publicWidget.Widget.extend({
    selector: '.o_portal_partner_details',
    events: {
		'change select[name="application_type"]': '_onApplicationTypeChange',
		'change #passport_photo': '_onPassportPhotoChange',
		'change select[name="citizenship"]': '_onCitizenshipChange',
    },

    /**
     * @override
     */
    start: function () {
        var def = this._super.apply(this, arguments);
        return def;
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

	/**
     * Show Voter ID details if selected Application type is Transfer Application
     *
     * @private
     */
    _onApplicationTypeChange: function () {
       var application_type = this.$('select[name="application_type"]');
		if(application_type.val() == 'Transfer Application'){
			document.getElementById('nav_tabs_link_voter').style.display = "block";
			document.getElementById('nav_tabs_content_voter').style.display = "block";
		}
		else{
			document.getElementById('nav_tabs_link_voter').style.display = "none";
			document.getElementById('nav_tabs_content_voter').style.display = "none";
		}
    },

	/**
     * Restrict the size of a file upload
     *
     * @private
     */
	_onPassportPhotoChange: function (ev) {
		var file = ev.target.files[0];
	  	var fileSize = file.size / 1024 / 1024; // in MiB
  		if (fileSize > 2) {
			Dialog.alert(null, "File is too big. File size cannot exceed 2MB.");
        	document.getElementById("passport_photo").value = "";
		}
	},

	/**
     * Show Passport Number field if selected Citizenship is Overseas
     *
     * @private
     */
	_onCitizenshipChange: function () {
       var citizenship = this.$('select[name="citizenship"]');
		if(citizenship.val() == 'Overseas'){
			$('.passport_field').removeClass('d-none');
		}
		else{
			$('.passport_field').addClass('d-none');
		}
    },
});
});
