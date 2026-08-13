/*  ---------------------------------------------------
    Theme Name: Staging
    Description: Staging bootstrap tamplate
    Author: Colorib
    Author URI: https://www.colorib.com/
    Version: 1.0
    Created: Colorib
---------------------------------------------------------  */

'use strict';

// Prevent native browser scroll jump on cross-page hash navigation
if (window.location.hash) {
    if ('scrollRestoration' in history) {
        history.scrollRestoration = 'manual';
    }
    window.scrollTo(0, 0);
}

(function ($) {

    /*------------------
        Preloader & Hash Navigation Fix
    --------------------*/
    function alignHashTarget() {
        if (!window.location.hash) return;
        var hash = window.location.hash;
        var $target = $(hash);
        if ($target.length) {
            var targetTop = Math.round($target.offset().top);
            var currentScroll = Math.round($(window).scrollTop());
            if (Math.abs(currentScroll - targetTop) > 5) {
                window.scrollTo(0, targetTop);
            }
        }
    }

    window.alignHashTarget = alignHashTarget;

    $(window).on('load', function () {
        alignHashTarget();
        $(".loader").fadeOut();
        $("#preloder").delay(150).fadeOut("slow", function () {
            alignHashTarget();
            setTimeout(alignHashTarget, 100);
            setTimeout(alignHashTarget, 300);
            setTimeout(alignHashTarget, 600);
        });
    });

    /*------------------
        Smooth In-Page Anchor Scroll
    --------------------*/
    $(document).on('click', 'a[href*="#"]', function (e) {
        var href = $(this).attr('href');
        var hash = this.hash;
        if (!hash || hash === '#') return;
        
        var cleanCurrent = window.location.pathname.replace(/\/$/, '').replace(/\/index\.html$/, '');
        var rawLink = (this.pathname || href.split('#')[0]);
        var cleanLink = rawLink.replace(/\/$/, '').replace(/\/index\.html$/, '').replace(/^index\.html$/, '');
        
        var isSamePage = (cleanCurrent === cleanLink || cleanLink === '' || cleanLink === '.');

        if (isSamePage) {
            var $target = $(hash);
            if ($target.length) {
                e.preventDefault();

                // Auto-close offcanvas mobile menu & Slicknav
                $(".offcanvas-menu-wrapper").removeClass("active");
                $(".offcanvas-menu-overlay").removeClass("active");
                try {
                    $(".mobile-menu").slicknav("close");
                } catch(err) {}

                var targetTop = Math.round($target.offset().top);
                window.scrollTo({
                    top: targetTop,
                    behavior: 'smooth'
                });
                if (history.pushState) {
                    history.pushState(null, null, hash);
                }
            }
        }
    });

    /*------------------
        Background Set
    --------------------*/
    $('.set-bg').each(function () {
        var bg = $(this).data('setbg');
        $(this).css('background-image', 'url(' + bg + ')');
    });

    //Canvas Menu
    $(".canvas__open").on('click', function () {
        $(".offcanvas-menu-wrapper").addClass("active");
        $(".offcanvas-menu-overlay").addClass("active");
    });

    $(".offcanvas-menu-overlay").on('click', function () {
        $(".offcanvas-menu-wrapper").removeClass("active");
        $(".offcanvas-menu-overlay").removeClass("active");
    });

    // Close mobile offcanvas menu on link click
    $(document).on('click', '.offcanvas-menu-wrapper a, .slicknav_nav a', function () {
        $(".offcanvas-menu-wrapper").removeClass("active");
        $(".offcanvas-menu-overlay").removeClass("active");
        try {
            $(".mobile-menu").slicknav("close");
        } catch(err) {}
    });


    /*------------------
		Navigation
	--------------------*/
    $(".mobile-menu").slicknav({
        prependTo: '#mobile-menu-wrap',
        allowParentLinks: true,
        closeOnClick: true
    });

    /*-----------------------
        Hero Slider
    ------------------------*/
    $(".hero__slider").owlCarousel({
        loop: false, // Set this to false
        margin: 0,
        items: 1,
        dots: true,
        nav: true,
        navText: ["<i class='fa fa-angle-left'><i/>", "<i class='fa fa-angle-right'><i/>"],
        animateOut: 'fadeOut',
        animateIn: 'fadeIn',
        smartSpeed: 1500,
        autoHeight: false,
        autoplay: true,
        mouseDrag: false,
		touchDrag: false, // Add this line to explicitly disable touch dragging
        onInitialized: function (e) {
            var a = this.items().length;
            $("#snh-1").html("<span>01</span><span>" + "0" + a + "</span>");
            var presentage = Math.round((100 / a));
            $('.slider__progress span').css("width", presentage + "%");
        }
    }).on("changed.owl.carousel", function (e) {
        var b = --e.item.index,
            a = e.item.count;
        $("#snh-1").html("<span> " + "0" + (1 > b ? b + a : b > a ? b - a : b) + "</span><span>" + "0" + a + "</span>");

        var current = e.page.index + 1;
        var presentage = Math.round((100 / e.page.count) * current);
        $('.slider__progress span').css("width", presentage + "%");
    });

    /*--------------------------
        Project Slider
    ----------------------------*/
    $(".project__slider").owlCarousel({
        loop: true,
        margin: 0,
        items: 4,
        dots: false,
        nav: true,
        navText: ["<span class='arrow_carrot-left'><span/>", "<span class='arrow_carrot-right'><span/>"],
        smartSpeed: 1200,
        autoHeight: false,
        autoplay: false,
        responsive: {
            320: {
                items: 1
            },
            768: {
                items: 2
            },
            992: {
                items: 3
            },
            1200: {
                items: 4
            }
        }
    });

    /*-----------------------------
        Testimonial Slider
    -------------------------------*/
    $('.testimonial__carousel').slick({
        slidesToShow: 1,
        slidesToScroll: 1,
        arrows: true,
        fade: true,
        // autoplay:true,
        asNavFor: '.testimonial__client',
        prevArrow: '<button type="button" class="slick-prev"><i class="fa fa-angle-left"><i></i></i></button>',
        nextArrow: '<button type="button" class="slick-next"><i class="fa fa-angle-right"><i></i></i></button>',
      });
      $('.testimonial__client').slick({
        slidesToShow: 4,
        slidesToScroll: 1,
        asNavFor: '.testimonial__carousel',
        arrows: false,
        variableWidth: true,
        centerMode: true,
        focusOnSelect: true,
        responsive: [
            {
              breakpoint: 768,
              settings: {
                slidesToShow: 3,
              }
            },
            {
              breakpoint: 575,
              settings: {
                slidesToShow: 1,
                slidesToScroll: 1,
                variableWidth: false
              }
            }
          ]
        
      });

    /*---------------------------------
        Logo Carousel
    ----------------------------------*/
    function hideClippedLogos() {
        var $carousel = $(".logo__carousel");
        var $outer = $carousel.find(".owl-stage-outer");
        if (!$outer.length) return;
        
        // Force fully visible opacity on mobile (width < 768px) and bypass clipping logic
        if ($(window).width() < 768) {
            $carousel.find(".owl-item").css({
                "opacity": "1",
                "pointer-events": "auto"
            });
            return;
        }
        
        var outerRight = $outer.offset().left + $outer.width();
        var outerLeft = $outer.offset().left;
        
        $carousel.find(".owl-item").each(function() {
            var $item = $(this);
            var itemLeft = $item.offset().left;
            var itemRight = itemLeft + $item.width();
            
            // Check if item is cut off by left or right boundary
            if (itemRight > outerRight + 5 || itemLeft < outerLeft - 5) {
                $item.css({
                    "opacity": "0",
                    "transition": "opacity 0.4s ease",
                    "pointer-events": "none"
                });
            } else {
                $item.css({
                    "opacity": "1",
                    "transition": "opacity 0.4s ease",
                    "pointer-events": "auto"
                });
            }
        });
    }

    $(".logo__carousel").owlCarousel({
        loop: true,
        dots: false,
        nav: false,
        smartSpeed: 1200,
        autoHeight: false,
        autoplay: true,
        responsive: {
            0: {
                items: 1,
                autoWidth: false,
                margin: 0
            },
            768: {
                autoWidth: true,
                margin: 80
            }
        },
        onInitialized: function() {
            setTimeout(hideClippedLogos, 100);
        },
        onTranslate: hideClippedLogos,
        onTranslated: hideClippedLogos,
        onResize: hideClippedLogos,
        onDragged: hideClippedLogos
    });

    $(window).on("resize", hideClippedLogos);

    /*---------------------------------
        Clear Stale Focus on Back Navigation (BFCache)
    ----------------------------------*/
    $(window).on('pageshow', function (event) {
        if (document.activeElement && typeof document.activeElement.blur === 'function') {
            document.activeElement.blur();
        }
        $('.product-cat-card, .rel-card, .rel-card *, .rel-card-btn, .rel-card-img').blur();
    });

    /*---------------------------------
        Category & Related Carousel 1-Tap Mobile Navigation Guard
    ----------------------------------*/
    (function () {
        var startX = 0, startY = 0;
        var cardSelector = '.categories-carousel .product-cat-card, .related-products-carousel .rel-card';
        
        $(document).on('touchstart', cardSelector, function (e) {
            if (e.originalEvent && e.originalEvent.touches && e.originalEvent.touches[0]) {
                startX = e.originalEvent.touches[0].clientX;
                startY = e.originalEvent.touches[0].clientY;
            }
        });

        $(document).on('touchend', cardSelector, function (e) {
            var $card = $(this);
            var $link = $(e.target).closest('a');
            if (!$link.length) {
                $link = $card.is('a') ? $card : $card.find('a').first();
            }
            var href = $link.attr('href');
            if (!href || href === '#' || href.indexOf('javascript:') === 0) return;

            var endX = startX, endY = startY;
            if (e.originalEvent && e.originalEvent.changedTouches && e.originalEvent.changedTouches[0]) {
                endX = e.originalEvent.changedTouches[0].clientX;
                endY = e.originalEvent.changedTouches[0].clientY;
            }

            var deltaX = Math.abs(endX - startX);
            var deltaY = Math.abs(endY - startY);

            // If displacement is less than 10px, treat as a clean tap (not a swipe drag)
            if (deltaX < 10 && deltaY < 10) {
                if (document.activeElement && typeof document.activeElement.blur === 'function') {
                    document.activeElement.blur();
                }
                window.location.href = href;
            }
        });
    })();

})(jQuery);
