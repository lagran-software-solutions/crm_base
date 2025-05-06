(function ($) {
	"use strict";

	/*------------------------------------
			Preloader
		--------------------------------------*/

	$(window).on('load', function () {
		$('#preloader').delay(350).fadeOut('slow');
		$('body').delay(350).css({ 'overflow': 'visible' });
	});



	/*------------------------------------
		Mobile Menu
	--------------------------------------*/

	$('#mobile-menu-active').metisMenu();

	$('#mobile-menu-active .has-dropdown > a').on('click', function (e) {
		e.preventDefault();
	});

	$(".hamburger-menu > a").on("click", function (e) {
		e.preventDefault();
		$(".slide-bar").toggleClass("show");
		$("body").addClass("on-side");
		$('.body-overlay').addClass('active');
		$(this).addClass('active');
	});

	$(".close-mobile-menu > a").on("click", function (e) {
		e.preventDefault();
		$(".slide-bar").removeClass("show");
		$("body").removeClass("on-side");
		$('.body-overlay').removeClass('active');
		$('.hamburger-menu > a').removeClass('active');
	});

	$('.body-overlay').on('click', function () {
		$(this).removeClass('active');
		$(".slide-bar").removeClass("show");
		$("body").removeClass("on-side");
		$('.hamburger-menu > a').removeClass('active');
	});

	/* Search
		-------------------------------------------------------*/
	var $searchWrap = $('.search-wrap');
	var $navSearch = $('.nav-search');
	var $searchClose = $('#search-close');

	$('.search-trigger').on('click', function (e) {
		e.preventDefault();
		$searchWrap.animate({ opacity: 'toggle' }, 500);
		$navSearch.add($searchClose).addClass("open");
	});

	$('.search-close').on('click', function (e) {
		e.preventDefault();
		$searchWrap.animate({ opacity: 'toggle' }, 500);
		$navSearch.add($searchClose).removeClass("open");
	});

	function closeSearch() {
		$searchWrap.fadeOut(200);
		$navSearch.add($searchClose).removeClass("open");
	}

	$(document.body).on('click', function (e) {
		closeSearch();
	});

	$(".search-trigger, .main-search-input").on('click', function (e) {
		e.stopPropagation();
	});


	//sticky-menu
	$(window).on('scroll', function () {
		var scroll = $(window).scrollTop();
		if (scroll < 200) {
			$(".main-header-area").removeClass("sticky-menu");
		} else {
			$(".main-header-area").addClass("sticky-menu");
		}
	});

	//hide and show sticky menu

	// var prevScrollpos = window.pageYOffset;
	// window.onscroll = function () {
	// 	var currentScrollPos = window.pageYOffset;
	// 	if (prevScrollpos > currentScrollPos) {
	// 		document.getElementById("hideshow-sticky-menu").style.top = "0";

	// 	} else {
	// 		document.getElementById("hideshow-sticky-menu").style.top = "-250px";
	// 		$(window).on('scroll', function () {
	// 			var scroll = $(window).scrollTop();
	// 			if (scroll < 200) {
	// 				$(".main-header-area").removeClass("sticky-menu");
	// 			} else {
	// 				$(".main-header-area").addClass("sticky-menu");
	// 			}
	// 		});
	// 	}
	// 	prevScrollpos = currentScrollPos;
	// }



	$('.sliders-active').owlCarousel({
		loop: true,
		margin: 10,
		dots: false,
		nav: true,
		navText: ['<i class="fal fa-long-arrow-left"></i>', '<i class="fal fa-long-arrow-right"></i>'],
		mouseDrag: false,
		autoplay: true,
		animateIn: 'fadeIn',
		responsive: {
			0: {
				items: 1,
				nav: false,
			},
			600: {
				items: 1,
				nav: false,
			},
			1000: {
				items: 1,
				nav: false,
			},
			1200: {
				items: 1
			}
		}
	});


	$('.sliders-active2').owlCarousel({
		loop: true,
		margin: 10,
		dots: false,
		nav: true,
		navText: ['<i class="fal fa-long-arrow-left"></i>', '<i class="fal fa-long-arrow-right"></i>'],
		mouseDrag: false,
		autoplay: true,
		autoplaySpeed: 5000,
		animateIn: 'slideIn',
		responsive: {
			0: {
				items: 1,
				nav: false,
			},
			600: {
				items: 1,
				nav: false,
			},
			1000: {
				items: 1,
				nav: false,
			},
			1200: {
				items: 1
			}
		}
	});


	// deal-active
	$('.brand-active').owlCarousel({
		loop: true,
		margin: 30,
		items: 5,
		autoplay: true,
		autoplaySpeed: 2000,
		nav: false,
		dots: false,
		navText: ['<i class="fal fa-long-arrow-left"></i>', '<i class="fal fa-long-arrow-right"></i>'],
		responsive: {
			0: {
				items: 1,
				margin: 0,
				nav: false
			},
			600: {
				items: 3,
			},
			980: {
				items: 4,
			},
			1200: {
				items: 5,
			},
		}
	})


	// brand-logo-1
	$('.portfolio-slide').owlCarousel({
		loop: true,
		margin: 30,
		items: 4,
		autoplay: true,
		autoplaySpeed: 2000,
		nav: true,
		dots: false,
		navText: ['<i class="fal fa-long-arrow-left"></i>', '<i class="fal fa-long-arrow-right"></i>'],
		responsive: {
			0: {
				items: 1,
				margin: 0,
				nav: false
			},
			600: {
				items: 2,
				nav: false
			},
			980: {
				items: 3,
			},
			1200: {
				items: 4,
			},
		}
	})


	// brand-logo-1
	$('.portfolio-slide2').owlCarousel({
		loop: true,
		margin: 30,
		items: 4,
		autoplay: true,
		autoplaySpeed: 2000,
		nav: true,
		dots: false,
		navText: ['<i class="fal fa-long-arrow-left"></i>', '<i class="fal fa-long-arrow-right"></i>'],
		responsive: {
			0: {
				items: 1,
				margin: 0,
				nav: false
			},
			600: {
				items: 2,
				nav: false
			},
			920: {
				items: 3,
			},
			1200: {
				items: 3.7,
			},
		}
	})
	// testimonial-active
	$('.testimonial-active').owlCarousel({
		loop: true,
		margin: 30,
		items: 3,
		autoplay: true,
		autoplaySpeed: 2000,
		nav: false,
		dots: false,
		navText: ['<i class="fal fa-long-arrow-left"></i>', '<i class="fal fa-long-arrow-right"></i>'],
		responsive: {
			0: {
				items: 1,
				margin: 0,
				nav: false
			},
			980: {
				items: 3,
			}
		}
	})

	// testimonial-active
	$('.testimonial-active2').owlCarousel({
		loop: true,
		margin: 30,
		items: 2,
		autoplay: true,
		autoplaySpeed: 2000,
		nav: false,
		dots: false,
		navText: ['<i class="fal fa-long-arrow-left"></i>', '<i class="fal fa-long-arrow-right"></i>'],
		responsive: {
			0: {
				items: 1,
				margin: 0,
				nav: false
			},
			600: {
				items: 1,
			},
			768: {
				items: 1,
			},
			980: {
				items: 2,
			}
		}
	})

	

	// blog-active
	$('.blog-active').owlCarousel({
		loop: true,
		margin: 30,
		items: 3,
		autoplay: true,
		autoplaySpeed: 2000,
		nav: true,
		dots: false,
		navText: ['<i class="fal fa-long-arrow-left"></i>', '<i class="fal fa-long-arrow-right"></i>'],
		responsive: {
			0: {
				items: 1,
				margin: 0,
				nav: false
			},
			600: {
				items: 2,
			},
			980: {
				items: 3,
			}
		}
	})
	// blog-active
	$('.blog-img-active').owlCarousel({
		loop: true,
		margin: 30,
		items: 1,
		autoplay: true,
		autoplaySpeed: 2000,
		nav: true,
		dots: false,
		navText: ['<i class="fal fa-arrow-left"></i>', '<i class="fal fa-arrow-right"></i>'],
		responsive: {
			0: {
				items: 1,
				margin: 0,
				nav: false
			},
			600: {
				items: 1,
			},
			980: {
				items: 1,
			}
		}
	})




	// Timeline Scroll Section
	// --------------------------------------------------------------
	var items = $(".reacttimeline li, .journey-list li"),
	timelineHeight = $(".timeline ul").height(),
	greyLine = $('.default-line'),
	lineToDraw = $('.draw-line');

	if(lineToDraw.length) {
	  	$(window).on('scroll', function () {

	    var redLineHeight = lineToDraw.height(),
	    greyLineHeight = greyLine.height(),
	    windowDistance = $(window).scrollTop(),
	    windowHeight = $(window).height() / 2,
	    timelineDistance = $(".reacttimeline").offset().top;

		    if(windowDistance >= timelineDistance - windowHeight) {
		      	var line = windowDistance - timelineDistance + windowHeight;
		      	if(line <= greyLineHeight) {
			        lineToDraw.css({
			          'height' : line + 20 + 'px'
			        });
		      	}
		    }

		    var bottom = lineToDraw.offset().top + lineToDraw.outerHeight(true);
		    items.each(function(index){
		      var circlePosition = $(this).offset();
		      	if(bottom > circlePosition.top) {				
		        	$(this).addClass('in-view');
		      	} else {
		        	$(this).removeClass('in-view');
		      	}
		    });	
	  	});
	}



	// -------------------- Remove Placeholder When Focus Or Click
	$("input,textarea").each(function () {
		$(this).data('holder', $(this).attr('placeholder'));
		$(this).on('focusin', function () {
			$(this).attr('placeholder', '');
		});
		$(this).on('focusout', function () {
			$(this).attr('placeholder', $(this).data('holder'));
		});
	});


	/* magnificPopup video view */
	$('.popup-video').magnificPopup({
		type: 'iframe'
	});


	// isotop
	$('.grid').imagesLoaded(function () {
		// init Isotope
		var $grid = $('.grid').isotope({
			itemSelector: '.grid-item',
			percentPosition: true,
			masonry: {
				// use outer width of grid-sizer for columnWidth
				columnWidth: 0,
				gutter: 0
			}
		});
		// filter items on button click
		$('.portfolio-menu').on('click', 'button', function () {
			var filterValue = $(this).attr('data-filter');
			$grid.isotope({ filter: filterValue });
		});
	});

	//for menu active class
	$('.portfolio-menu button').on('click', function (event) {
		$(this).siblings('.active').removeClass('active');
		$(this).addClass('active');
		event.preventDefault();
	});

	//counter
	$('.counter').counterUp({
		delay: 10,
		time: 3000
	});


	// scrollToTop
	$.scrollUp({
		scrollName: 'scrollUp', // Element ID
		topDistance: '300', // Distance from top before showing element (px)
		topSpeed: 500, // Speed back to top (ms)
		animation: 'fade', // Fade, slide, none
		animationInSpeed: 300, // Animation in speed (ms)
		animationOutSpeed: 300, // Animation out speed (ms)
		scrollText: '<i class="fas fa-chevron-double-up"></i>', // Text for element
		activeOverlay: false, // Set CSS color to display scrollUp active point, e.g '#00FFFF'
	});


	// wow animation - start
	// --------------------------------------------------
	function wowAnimation() {
		new WOW({
			offset: 100,
			mobile: true
		}).init()
	}
	wowAnimation();



	//nice-select
	$(document).ready(function () {
		$('select').niceSelect();
	});



	// onepage-scroll
	var singlepage = $('.single-page-nav');

	if(singlepage.length) {
		$('.single-page-nav').singlePageNav({
		offset: $('.single-page-nav').outerHeight(),
		threshold: 120,
		speed: 400,
		currentClass: 'current',
		easing: 'swing',
		filter: ':not(.external)',
		onComplete: function() {
		console.log('done scrolling');
		}
		});
	}
	
	// slidebar hide
	var singlepage1 = $('.side-mobile-menu-onpage');
	if(singlepage1.length){
		$(".side-mobile-menu-onpage a").on("click", function () {
			$(".slide-bar").removeClass("show");
			$(".body-overlay").removeClass("active");
		});
	}

})(jQuery);