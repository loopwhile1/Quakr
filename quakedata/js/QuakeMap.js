YUI().use('node', 'json', 'io', function (Y) {

    // Takes an ISO time and returns a string representing how
    // long ago the date represents.
    function prettyDate(time){
        var date = new Date((time || "").replace(/-/g,"/").replace(/[TZ]/g," ")),
            diff = (((new Date()).getTime() - date.getTime()) / 1000),
            day_diff = Math.floor(diff / 86400);
			
        if ( isNaN(day_diff) || day_diff < 0 || day_diff >= 31 )
            return;
			
        return day_diff == 0 && (
			diff < 60 && "just now" ||
			diff < 120 && "1 minute ago" ||
			diff < 3600 && Math.floor( diff / 60 ) + " minutes ago" ||
			diff < 7200 && "1 hour ago" ||
			diff < 86400 && Math.floor( diff / 3600 ) + " hours ago") ||
            day_diff == 1 && "Yesterday" ||
            day_diff < 7 && day_diff + " days ago" ||
            day_diff < 31 && Math.ceil( day_diff / 7 ) + " weeks ago";
    }


	inherit = function(p) {
		if (p == null) throw TypeError(); 			// p must be a non-null object
		if (Object.create) return Object.create(p); // Use it if available
		var t = typeof p;							// More type checking because I can.
		if (t != "object" && t !== "function") throw TypeError();
		function f() {}								// create dummy function
		f.prototype = p;							// set the prototype to p
		return new f();								// Use f() to create an "heir" of p.
	}

	//+----------------------------------------------------------------------------------
	//
	//  Member:     earthQuakeFetcher
	//
	//  Synopsis:   Responsible for fetching & parsing the earth quake
	//
	//-----------------------------------------------------------------------------------
    var earthQuakeFetcher = {
        ajaxObj : null,         // holds YUI.io object, so we can abort the ajax call if needed.
        resultHandler: null,    // reference to the most-recent resultHandler object.
        delegate : null,
        // Private function to get the fetch url
        getEarthQuakeUrl_ : function() {
            return '/getQuakes'
        },
        
        // Fetch notification
        getEarthQuakeData : function() {
            
            // Get the url
            url = this.getEarthQuakeUrl_();
            
            // Create the io callback/configuration
            var callback = {
                timeout: 10000,
                context: this,
                on: {
                    success: function(x, o) {
                        this.ajaxSuccess(x,o);
                    },
                    
                    failure: function(x, o) {
                        this.ajaxFailure(x,o);
                    }
                }
            };
            
            // Abort previous request
            this.abortAjax();
            
            // Start a new ajax request
            this.ajaxObj = Y.io(url, callback);
        },
        
        abortResultHandler : function() {
        	if( this.resultHandler ) {
        		this.resultHandler.cancel()
        	}
        },
        
        //-----------------------------------------------------------------------------------
        // #pragma mark - Ajax callbacks & utilities
        //-----------------------------------------------------------------------------------
        
        isFetchingResults : function() {
            return ( this.ajaxObj && this.ajaxObj.abort && this.ajaxObj.isInProgress() );
        },
        
        abortAjax : function() {
            if( this.isFetchingResults() ) {
                console.warn('ABORT!');
                this.ajaxObj.abort();
            }
        },
        
        ajaxSuccess : function(x, o) {
            this.abortResultHandler();
            this.resultHandler = new EarthQuakesResultHandler(x, o, this);
        },
        
        ajaxFailure : function(x,o ) {
            
        },
        
        //-----------------------------------------------------------------------------------
        // #pragma mark - EarthQuakeResultHandler delegate implementation
        //-----------------------------------------------------------------------------------
        earthQuakesParsedSuccessfully : function(earthQuakesResultHandler)
        {
			earthQuakes = earthQuakesResultHandler.getEarthQuakes();
			this.delegate.earthQuakesParsed(earthQuakes);
        },
        
        earthQuakesParseFailed : function(earthQuakesResultHandler)
        {   
        }
    };
    
    //+----------------------------------------------------------------------------------
	//
	//  Member:     EarthQuakesResultHandler
	//
	//  Synopsis:   Parses the notifications json
	//
	//-----------------------------------------------------------------------------------
    var EarthQuakesResultHandler = function(x, o, delegate) {
        var jsonObj;
        this.results = null;
        
	    try {
	        jsonObj = Y.JSON.parse(o.responseText);
			// TODO: catch error. find error?
    		this.results = jsonObj ? jsonObj : [];
	    } 
	    catch(e) {
			if (delegate != undefined) {
				delegate.earthQuakesParseFailed(this);
			}
	        console.error("AJAX/server error", e);
	        return;
	    }
	    
		if (delegate != undefined) {
			delegate.earthQuakesParsedSuccessfully(this);
		}
    }
    
    EarthQuakesResultHandler.prototype.cancel = function() {
	}
	
	EarthQuakesResultHandler.prototype.getEarthQuakes = function () {
	    return this.results;
	}
   
	var earthQuakeMap = {
		map : null,
		markers : [],
		currentInfoWindow : null,
		initializeMap : function()  {
			var myOptions = {
			  zoom: 4,
			  center: new google.maps.LatLng(47.397, -122.644),
			  mapTypeId: google.maps.MapTypeId.ROADMAP
			};
			this.map = new google.maps.Map(document.getElementById('map_canvas'), myOptions);
			earthQuakeFetcher.delegate = earthQuakeMap;
			earthQuakeFetcher.getEarthQuakeData();
		},
		
		addMarker : function(position) {
			this.markers.push(new google.maps.Marker({
			  position: position,
			  map: map,
			  draggable: false
			}));
			return this.markers[this.markers.length-1];
		},
		
		addCallout : function(marker, message) {
			var that = this;
			google.maps.event.addListener(marker, 'click', function() {
				if (that.currentInfoWindow) that.currentInfoWindow.close();
				that.currentInfoWindow = new google.maps.InfoWindow({
					content: message
					});
				that.currentInfoWindow.open(marker.get('map'), marker);
			});
		},
		
		getInfoWindow : function(quake) {
			var templateHtml = document.getElementById("info-window-template").innerHTML;
            var template = Handlebars.compile(templateHtml);
			quake.date = prettyDate(quake.date);
			console.log(quake);
    		var result = template(quake);
			return result
		},
		
		earthQuakesParsed : function (quakes) {
			for (i=0; i<quakes.length; i++) {
				var quake = quakes[i];
				var marker = this.addMarker(new google.maps.LatLng(quake.geoPoint.lat, quake.geoPoint.lon));
				this.addCallout(marker, this.getInfoWindow(quake));
			}
		}
	};
	
	google.maps.event.addDomListener(window, 'load',earthQuakeMap.initializeMap);
});