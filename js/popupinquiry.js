/*
 * JavaScript for the Inquiry Popup Functionality
 * Insert this just before the closing </body> tag in your index.html
 */
document.addEventListener('DOMContentLoaded', function() {
    const inquiryContainer = document.getElementById('inquiryContainer');
    const toggleButton = document.getElementById('inquiryToggleButton');
    const closeFormButton = document.getElementById('closeInquiryForm');
    const inquiryForm = document.getElementById('inquiryForm');
    const permanentCloseButton = document.getElementById('permanentCloseInquiryButton');

    // Get the new elements for dynamic subject
    const inquiryNameInput = document.getElementById('inquiryName');
    const inquiryDynamicSubjectField = document.getElementById('inquiryDynamicSubject');

    // Get references for the overlay elements using querySelector for reliability
    const inquiryOverlay = document.querySelector('.inquiry-overlay');
    const inquirySpinner = document.querySelector('.inquiry-overlay .spinner'); // Specific selector for spinner within overlay
    const overlayMessage = document.querySelector('.inquiry-overlay .overlay-message'); // Specific selector for message within overlay
    const formBlurArea = document.querySelector('.form-blur-area'); // Target the blur area by its class


    let shrinkTimer;
    let collapseTimer = null; // Renamed for clarity, similar to buttontest.html
    let shakeInterval;
    let touchHoldTimeout;
    let isHolding = false; // Flag to differentiate between tap and hold on mobile

    const SHAKE_DURATION = 500; // milliseconds
    const SHAKE_INTERVAL_DELAY = 2000; // milliseconds (2 seconds)
    const COLLAPSE_DELAY = 10000; // milliseconds (10 seconds) for auto-collapse
    const TOUCH_HOLD_DELAY = 350; // milliseconds for touch hold to expand

    // Define the desktop breakpoint. This should match your CSS media query.
    const DESKTOP_BREAKPOINT = 768;

    // Function to add the 'collapsed' class and start shaking (if applicable)
    function collapseButtonAndStartShaking() {
        // Only collapse if the form is NOT open, the container is NOT permanently hidden,
        // AND it's a mobile screen size.
        if (window.innerWidth <= DESKTOP_BREAKPOINT && !inquiryContainer.classList.contains('active') && !inquiryContainer.classList.contains('hidden')) {
            toggleButton.classList.add('collapsed'); // Use 'collapsed' class
            startShaking(); // Shaking can still apply to the collapsed button
        }
    }

    // Function to remove the 'collapsed' class and stop shaking
    function expandButtonAndStopShaking() {
        toggleButton.classList.remove('collapsed'); // Remove 'collapsed' class
        stopShaking();
    }

    // Function to start the shaking animation
    function startShaking() {
        stopShaking(); // Clear any existing shake interval first
        shakeInterval = setInterval(() => {
            // Shake if the button is not active (form not open)
            // This applies to both collapsed (mobile) and wide (desktop/mobile uncollapsed) states.
            if (!inquiryContainer.classList.contains('active')) {
                toggleButton.classList.add('shake-animation');
                setTimeout(() => {
                    toggleButton.classList.remove('shake-animation');
                }, SHAKE_DURATION);
            }
        }, SHAKE_INTERVAL_DELAY);
    }

    // Function to stop the shaking animation
    function stopShaking() {
        clearInterval(shakeInterval);
        toggleButton.classList.remove('shake-animation'); // Ensure animation class is removed
    }

    // Function to reset the collapse timer (will cause it to collapse after delay if not interacted with)
    function resetCollapseTimer() {
        clearTimeout(collapseTimer);
        // Only set the timer if on a mobile screen
        if (window.innerWidth <= DESKTOP_BREAKPOINT) {
            collapseTimer = setTimeout(collapseButtonAndStartShaking, COLLAPSE_DELAY);
        }
    }

    // Function to toggle the visibility of the inquiry form popup
    function toggleInquiryForm() {
        inquiryContainer.classList.toggle('active');
        if (inquiryContainer.classList.contains('active')) {
            // If form is open, stop shaking and ensure button is expanded
            expandButtonAndStopShaking(); // Ensure expanded when form is open
            clearTimeout(collapseTimer); // Do not collapse while form is open
        } else {
            // If form is closed, reset collapse timer (will collapse after delay)
            resetCollapseTimer();
            // Start shaking immediately when the form closes, regardless of desktop/mobile,
            // as per new requirement for desktop shake.
            startShaking();
        }
    }

    // Function to hide the entire inquiry button container until page reload
    function hideEntireInquiryButton() {
        // Ensure the form is closed first if it's currently open
        if (inquiryContainer.classList.contains('active')) {
            inquiryContainer.classList.remove('active');
        }
        // Add the 'hidden' class to make the entire container disappear
        inquiryContainer.classList.add('hidden');
        clearTimeout(collapseTimer); // Stop all timers related to button state
        stopShaking();
    }

    // Event listener for the main toggle button (to open/close the form)
    if (toggleButton) {
        toggleButton.addEventListener('click', function(event) {
            // Only toggle form if it wasn't a mobile touch hold that just ended
            if (isHolding) {
                isHolding = false; // Reset flag
                event.preventDefault(); // Prevent click from firing if hold was detected
                return;
            }
            toggleInquiryForm();
        });
    }

    // Event listener for the close button inside the form
    if (closeFormButton) {
        closeFormButton.addEventListener('click', toggleInquiryForm);
    }

    // Event listener for the new permanent 'x' button on the toggle bar itself
    if (permanentCloseButton) {
        permanentCloseButton.addEventListener('click', function(event) {
            event.stopPropagation(); // Prevents the click on 'x' from also triggering the toggle button
            hideEntireInquiryButton(); // Hides the entire sticky button
        });
    }

    // Desktop Hover Effects (integrated with auto-collapse logic)
    // Check for window width to apply hover effects only on desktop-like screens
    if (window.innerWidth > DESKTOP_BREAKPOINT) { // Use the same breakpoint
        toggleButton.addEventListener('mouseenter', function() {
            clearTimeout(collapseTimer); // Stop pending collapse
            expandButtonAndStopShaking(); // Ensure expanded and shaking stops
        });

        toggleButton.addEventListener('mouseleave', function() {
            // On desktop, the button should remain expanded.
            // If form is closed, re-start shaking when mouse leaves.
            if (!inquiryContainer.classList.contains('active')) {
                startShaking(); // Start shaking again
            }
        });
    }


    // Mobile Touch Hold to Expand
    toggleButton.addEventListener('touchstart', function(event) {
        // Only start hold if on mobile and not already active (form not open)
        if (window.innerWidth <= DESKTOP_BREAKPOINT && !inquiryContainer.classList.contains('active')) {
            touchHoldTimeout = setTimeout(() => {
                isHolding = true; // Mark as holding
                toggleButton.classList.add('expanded-mobile'); // Add class to expand visually
                expandButtonAndStopShaking(); // Stop shaking and ensure it's fully expanded
                clearTimeout(collapseTimer); // Prevent auto-collapse while expanded by hold
            }, TOUCH_HOLD_DELAY);
        }
    }, { passive: true }); // Use passive listener for better scroll performance

    toggleButton.addEventListener('touchend', function(event) {
        clearTimeout(touchHoldTimeout); // Clear any pending hold timeout
        touchHoldTimeout = null; // Reset the timeout variable

        if (isHolding) {
            // If a hold was detected, collapse back after touch ends, unless form is now opened
            // And only if on mobile.
            if (window.innerWidth <= DESKTOP_BREAKPOINT && !inquiryContainer.classList.contains('active')) {
                toggleButton.classList.remove('expanded-mobile'); // Remove visual expansion
                resetCollapseTimer(); // Restart auto-collapse
                startShaking(); // Re-start shaking for mobile uncollapsed state
            }
            isHolding = false; // Reset hold flag
            // Prevent subsequent click event from firing immediately if a hold just ended
            // This is crucial to prevent the form from opening right after expanding from a hold.
            event.preventDefault();
        }
    });

    toggleButton.addEventListener('touchcancel', function(event) {
        clearTimeout(touchHoldTimeout);
        touchHoldTimeout = null;
        if (isHolding) {
            if (window.innerWidth <= DESKTOP_BREAKPOINT && !inquiryContainer.classList.contains('active')) {
                toggleButton.classList.remove('expanded-mobile');
                resetCollapseTimer();
                startShaking(); // Re-start shaking for mobile uncollapsed state
            }
            isHolding = false;
            event.preventDefault();
        }
    });


    // Event listener for form submission (MODIFIED for AJAX with error handling)
    if (inquiryForm) {
        inquiryForm.addEventListener('submit', function(event) {
            event.preventDefault(); // Prevent default form submission

            const form = event.target;

            // Set the dynamic subject before creating FormData
            const userName = inquiryNameInput.value.trim();
            inquiryDynamicSubjectField.value = userName ? `${userName} : Inquiry from Popup` : "Website Inquiry";

            const formData = new FormData(form);

            // Show overlay with spinner and "Sending message..."
            // Ensure elements exist before trying to manipulate them
            if (inquiryOverlay && inquirySpinner && overlayMessage && formBlurArea) {
                inquiryOverlay.classList.add('visible');
                inquirySpinner.style.display = 'block';
                overlayMessage.textContent = '⏳ Sending message...';
                overlayMessage.style.display = 'block';
                formBlurArea.classList.add('blurred'); // Blur the form content
            }
            
            const MIN_SENDING_MESSAGE_DISPLAY_DURATION = 3000; // 3 seconds for "Sending message..."
            const MIN_SUCCESS_ERROR_MESSAGE_DISPLAY_DURATION = 3000; // 3 seconds for success/error message

            const startTime = Date.now();

            fetch("https://formsubmit.co/ajax/c1d7227628041c568dbd62caac8ef5e7", { // Use the provided email and ?_ajax=true for AJAX mode
                method: "POST",
                body: formData
            })
            .then(response => {
                const fetchEndTime = Date.now();
                const actualSendingDuration = fetchEndTime - startTime;
                const remainingSendingDelay = Math.max(0, MIN_SENDING_MESSAGE_DISPLAY_DURATION - actualSendingDuration);

                // This promise ensures the "Sending message..." is shown for at least 3 seconds
                return new Promise(resolve => setTimeout(() => resolve(response), remainingSendingDelay));
            })
            .then(response => {
                // This block executes AFTER the "Sending message..." has been displayed for its minimum duration
                if (response.ok) {
                    if (overlayMessage) overlayMessage.textContent = "✅ Message sent successfully! Our Team will contact you shortly!";
                    if (inquirySpinner) inquirySpinner.style.display = 'none';
                    form.reset(); // Clear the form fields

                    // Now, show the success message for its minimum duration (3 seconds)
                    setTimeout(() => {
                        if (inquiryOverlay) inquiryOverlay.classList.remove('visible');
                        if (formBlurArea) formBlurArea.classList.remove('blurred'); // Unblur form
                    }, MIN_SUCCESS_ERROR_MESSAGE_DISPLAY_DURATION);
                } else {
                    // Attempt to read error message from response if available, otherwise use generic
                    response.json().then(data => {
                        if (overlayMessage) overlayMessage.textContent = `❌ Failed to send message: ${data.message || 'Unknown error'}`;
                    }).catch(() => {
                        if (overlayMessage) overlayMessage.textContent = "❌ Failed to send message.";
                    });
                    if (inquirySpinner) inquirySpinner.style.display = 'none';
                    
                    // Show the error message for its minimum duration (3 seconds)
                    setTimeout(() => {
                        if (inquiryOverlay) inquiryOverlay.classList.remove('visible');
                        if (formBlurArea) formBlurArea.classList.remove('blurred'); // Unblur form
                    }, MIN_SUCCESS_ERROR_MESSAGE_DISPLAY_DURATION); // Use same duration for error message
                }
            })
            .catch(error => {
                // This catch block handles network errors or issues with the fetch itself
                const fetchEndTime = Date.now();
                const actualSendingDuration = fetchEndTime - startTime;
                const remainingSendingDelay = Math.max(0, MIN_SENDING_MESSAGE_DISPLAY_DURATION - actualSendingDuration);

                setTimeout(() => {
                    if (overlayMessage) overlayMessage.textContent = "❌ Network error. Please try again.";
                    if (inquirySpinner) inquirySpinner.style.display = 'none';
                    
                    // Show the network error message for its minimum duration (3 seconds)
                    setTimeout(() => {
                        if (inquiryOverlay) inquiryOverlay.classList.remove('visible');
                        if (formBlurArea) formBlurArea.classList.remove('blurred'); // Unblur form
                    }, MIN_SUCCESS_ERROR_MESSAGE_DISPLAY_DURATION);
                }, remainingSendingDelay); // Ensure sending message was shown for min duration
            });
        });
    }

    // Optional: Close the inquiry form with the Escape key
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape' && inquiryContainer.classList.contains('active')) {
            toggleInquiryForm();
        }
    });

    // Optional: Close the inquiry form if clicking outside of it (but not on the toggle button itself)
    document.addEventListener('click', function(event) {
        if (inquiryContainer.classList.contains('active') &&
            !inquiryContainer.contains(event.target) &&
            event.target !== toggleButton) {
            toggleInquiryForm();
        }
    });

    // Initial call to start shaking when the page loads
    window.addEventListener('load', () => {
        // Start shaking on load for both desktop and mobile (if not hidden/active)
        if (!inquiryContainer.classList.contains('active') && !inquiryContainer.classList.contains('hidden')) {
            startShaking();
        }

        // If on mobile, also start the collapse timer
        if (window.innerWidth <= DESKTOP_BREAKPOINT) {
            collapseTimer = setTimeout(() => {
                collapseButtonAndStartShaking();
            }, COLLAPSE_DELAY);
        }
    });


    // Add an event listener for window resize to handle responsiveness
    window.addEventListener('resize', () => {
        if (window.innerWidth > DESKTOP_BREAKPOINT) {
            // If resized to desktop, ensure button is expanded and start shaking
            expandButtonAndStopShaking(); // Ensures it's wide and stops any pending mobile collapse
            clearTimeout(collapseTimer); // Clear mobile collapse timer
            toggleButton.classList.remove('expanded-mobile'); // Ensure this class is removed on desktop
            if (!inquiryContainer.classList.contains('active') && !inquiryContainer.classList.contains('hidden')) {
                startShaking(); // Start shaking for desktop
            }
        } else {
            // If resized to mobile, and form is not active, re-start collapse timer and shaking
            if (!inquiryContainer.classList.contains('active') && !inquiryContainer.classList.contains('hidden')) {
                resetCollapseTimer(); // Re-enable auto-collapse for mobile
                startShaking(); // Continue shaking for mobile (both collapsed and uncollapsed states)
            }
        }
    });
});
