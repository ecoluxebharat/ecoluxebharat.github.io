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
        if (!toggleButton || !inquiryContainer) return;
        if (window.innerWidth <= DESKTOP_BREAKPOINT && !inquiryContainer.classList.contains('active') && !inquiryContainer.classList.contains('hidden')) {
            toggleButton.classList.add('collapsed');
            startShaking();
        }
    }

    // Function to remove the 'collapsed' class and stop shaking
    function expandButtonAndStopShaking() {
        if (toggleButton) toggleButton.classList.remove('collapsed');
        stopShaking();
    }

    // Function to start the shaking animation
    function startShaking() {
        stopShaking();
        if (!toggleButton || !inquiryContainer) return;
        shakeInterval = setInterval(() => {
            if (!inquiryContainer.classList.contains('active')) {
                toggleButton.classList.add('shake-animation');
                setTimeout(() => {
                    if (toggleButton) toggleButton.classList.remove('shake-animation');
                }, SHAKE_DURATION);
            }
        }, SHAKE_INTERVAL_DELAY);
    }

    // Function to stop the shaking animation
    function stopShaking() {
        clearInterval(shakeInterval);
        if (toggleButton) toggleButton.classList.remove('shake-animation');
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
            // If opening via floating button and no product preview was set, hide product card preview
            const cardEl = document.getElementById('inquiryProductCard');
            const prodNameField = document.getElementById('inquiryProductName');
            if (prodNameField && prodNameField.value === "General Inquiry" && cardEl) {
                cardEl.style.display = 'none';
            }
            expandButtonAndStopShaking();
            clearTimeout(collapseTimer);
        } else {
            resetCollapseTimer();
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

    // Desktop Hover Effects & Touch listeners (only when toggleButton is present)
    if (toggleButton) {
        if (window.innerWidth > DESKTOP_BREAKPOINT) {
            toggleButton.addEventListener('mouseenter', function() {
                clearTimeout(collapseTimer);
                expandButtonAndStopShaking();
            });

            toggleButton.addEventListener('mouseleave', function() {
                if (!inquiryContainer.classList.contains('active')) {
                    startShaking();
                }
            });
        }

        toggleButton.addEventListener('touchstart', function(event) {
            if (window.innerWidth <= DESKTOP_BREAKPOINT && !inquiryContainer.classList.contains('active')) {
                touchHoldTimeout = setTimeout(() => {
                    isHolding = true;
                    toggleButton.classList.add('expanded-mobile');
                    expandButtonAndStopShaking();
                    clearTimeout(collapseTimer);
                }, TOUCH_HOLD_DELAY);
            }
        }, { passive: true });

        toggleButton.addEventListener('touchend', function(event) {
            clearTimeout(touchHoldTimeout);
            touchHoldTimeout = null;

            if (isHolding) {
                if (window.innerWidth <= DESKTOP_BREAKPOINT && !inquiryContainer.classList.contains('active')) {
                    toggleButton.classList.remove('expanded-mobile');
                    resetCollapseTimer();
                    startShaking();
                }
                isHolding = false;
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
                    startShaking();
                }
                isHolding = false;
            }
        });
    }

    // Modal-only backdrop click to close
    if (inquiryContainer) {
        inquiryContainer.addEventListener('click', function(event) {
            if (inquiryContainer.classList.contains('modal-only-mode') && event.target === inquiryContainer) {
                inquiryContainer.classList.remove('active');
            }
        });
    }

    // Helper: Customer Code generator for unique email subjects
    function getCustomerCode(name, phone) {
        const initials = (name || "").replace(/[^a-zA-Z]/g, "").substring(0, 2).toUpperCase() || "IN";
        const phoneDigits = (phone || "").replace(/\D/g, "");
        const last4 = phoneDigits.length >= 4 ? phoneDigits.slice(-4) : (phoneDigits || "0000");
        return `${initials}-${last4}`;
    }

    // Helper: Default message generator
    function getFormattedDefaultMessage(productName, quantity, unit) {
        let qtyStr = "";
        if (quantity && quantity.trim()) {
            qtyStr = `\nEstimated Quantity / Requirement: ${quantity.trim()} ${unit || 'Pcs'}`;
        }
        if (productName && productName !== "General Inquiry") {
            return `Hello EcoLuxe Bharat,\n\nI would like to request pricing, technical specifications, and delivery timelines for the following product model:\n\nProduct: ${productName}${qtyStr}\n\nPlease share the official catalog and quotation.`;
        }
        return `Hello EcoLuxe Bharat,\n\nI am interested in your road safety products and would like to request information regarding product specifications, pricing, and availability.\n\nPlease get in touch with me.`;
    }

    // Event listener for form submission (MODIFIED for AJAX with error handling & auto-close)
    if (inquiryForm) {
        inquiryForm.addEventListener('submit', function(event) {
            event.preventDefault(); // Prevent default form submission

            const form = event.target;

            const userName = inquiryNameInput ? inquiryNameInput.value.trim() : "";
            const productName = document.getElementById('inquiryProductName') ? document.getElementById('inquiryProductName').value : "General Inquiry";
            const productUnit = document.getElementById('inquiryProductUnitVal') ? document.getElementById('inquiryProductUnitVal').value : "Pcs";
            const quantityVal = document.getElementById('inquiryQuantity') ? document.getElementById('inquiryQuantity').value.trim() : "";
            const messageField = document.getElementById('inquiryMessage');

            // 1. If message textarea is empty or whitespace, populate generic dynamic inquiry message
            if (messageField && !messageField.value.trim()) {
                messageField.value = getFormattedDefaultMessage(productName, quantityVal, productUnit);
            }

            // 2. Set clear dynamic subject line with customer code for index.html popup form
            if (inquiryDynamicSubjectField) {
                const leadName = userName || "New Lead";
                const userPhone = form.querySelector('input[name="Phone Number"]') ? form.querySelector('input[name="Phone Number"]').value.trim() : "";
                const code = getCustomerCode(userName, userPhone);
                inquiryDynamicSubjectField.value = `${leadName} - General Inquiry - ${code}`;
            }

            // Set current Page URL
            const pageUrlField = document.getElementById('inquiryPageUrl');
            if (pageUrlField) {
                pageUrlField.value = window.location.href;
            }

            const formData = new FormData(form);

            // Show overlay with spinner and "Sending message..."
            if (inquiryOverlay && inquirySpinner && overlayMessage && formBlurArea) {
                inquiryOverlay.classList.add('visible');
                inquirySpinner.style.display = 'block';
                overlayMessage.textContent = '⏳ Sending message...';
                overlayMessage.style.display = 'block';
                formBlurArea.classList.add('blurred'); // Blur the form content
            }
            
            const MIN_SENDING_MESSAGE_DISPLAY_DURATION = 3000; // 3.0s minimum for sending message
            const MIN_SUCCESS_ERROR_MESSAGE_DISPLAY_DURATION = 3000; // 3.0s minimum for success message before auto-closing

            const startTime = Date.now();

            const targetUrl = (inquiryForm && inquiryForm.action) || window.FORMSUBMIT_URL || "https://formsubmit.co/ajax/temp2temp2222@gmail.com";
            fetch(targetUrl, {
                method: "POST",
                body: formData
            })
            .then(response => {
                const fetchEndTime = Date.now();
                const actualSendingDuration = fetchEndTime - startTime;
                const remainingSendingDelay = Math.max(0, MIN_SENDING_MESSAGE_DISPLAY_DURATION - actualSendingDuration);

                return new Promise(resolve => setTimeout(() => resolve(response), remainingSendingDelay));
            })
            .then(response => {
                if (response.ok) {
                    if (overlayMessage) overlayMessage.textContent = "✅ Message sent successfully! Our Team will contact you shortly!";
                    if (inquirySpinner) inquirySpinner.style.display = 'none';
                    form.reset(); // Clear form fields

                    // Auto-close modal after 3.0s
                    setTimeout(() => {
                        if (inquiryOverlay) inquiryOverlay.classList.remove('visible');
                        if (formBlurArea) formBlurArea.classList.remove('blurred');
                        if (inquiryContainer) inquiryContainer.classList.remove('active');
                    }, MIN_SUCCESS_ERROR_MESSAGE_DISPLAY_DURATION);
                } else {
                    response.json().then(data => {
                        if (overlayMessage) overlayMessage.textContent = `❌ Failed to send message: ${data.message || 'Unknown error'}`;
                    }).catch(() => {
                        if (overlayMessage) overlayMessage.textContent = "❌ Failed to send message.";
                    });
                    if (inquirySpinner) inquirySpinner.style.display = 'none';
                    
                    setTimeout(() => {
                        if (inquiryOverlay) inquiryOverlay.classList.remove('visible');
                        if (formBlurArea) formBlurArea.classList.remove('blurred');
                    }, MIN_SUCCESS_ERROR_MESSAGE_DISPLAY_DURATION);
                }
            })
            .catch(error => {
                const fetchEndTime = Date.now();
                const actualSendingDuration = fetchEndTime - startTime;
                const remainingSendingDelay = Math.max(0, MIN_SENDING_MESSAGE_DISPLAY_DURATION - actualSendingDuration);

                setTimeout(() => {
                    if (overlayMessage) overlayMessage.textContent = "❌ Network error. Please try again.";
                    if (inquirySpinner) inquirySpinner.style.display = 'none';
                    
                    setTimeout(() => {
                        if (inquiryOverlay) inquiryOverlay.classList.remove('visible');
                        if (formBlurArea) formBlurArea.classList.remove('blurred');
                    }, MIN_SUCCESS_ERROR_MESSAGE_DISPLAY_DURATION);
                }, remainingSendingDelay);
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

    // --- Dedicated Product Inquiry Modal Logic ---
    const productModal = document.getElementById('productInquiryModal');
    const closeProductModalBtn = document.getElementById('closeProductInquiryModal');
    const productBackdrop = document.getElementById('productInquiryBackdrop');
    const productInquiryForm = document.getElementById('productInquiryForm');

    let currentProductUnit = "Pcs";

    function openProductModal(productName, productImg, productTitle, productModel, productUnit, productCategory) {
        if (!productModal) return;

        currentProductUnit = productUnit || 'Pcs';

        // 1. Populate Preview Header
        const imgEl = document.getElementById('productModalImg');
        const titleEl = document.getElementById('productModalTitle');
        const modelEl = document.getElementById('productModalModel');

        if (imgEl) imgEl.src = productImg || "";
        if (titleEl) titleEl.textContent = productTitle || productName;
        if (modelEl) modelEl.textContent = productModel ? `Model: ${productModel}` : "";

        // 2. Set hidden metadata
        const nameHidden = document.getElementById('prodModalHiddenName');
        if (nameHidden) nameHidden.value = productName;

        const categoryHidden = document.getElementById('prodModalHiddenCategory');
        if (categoryHidden) categoryHidden.value = productCategory || "Road Safety";

        const urlHidden = document.getElementById('prodModalHiddenUrl');
        if (urlHidden) urlHidden.value = window.location.href;

        const subjectHidden = document.getElementById('prodModalHiddenSubject');
        if (subjectHidden) subjectHidden.value = `Inquiry: ${productName}`;

        // 3. Update quantity input placeholder
        const qtyInput = document.getElementById('prodModalQtyInput');
        if (qtyInput) {
            qtyInput.placeholder = "e.g. 50pcs";
            qtyInput.value = "";
        }

        // 4. Open Modal
        productModal.classList.add('active');
    }

    function closeProductModal() {
        if (!productModal) return;
        productModal.classList.remove('active');

        // Hide overlay if open
        const overlay = document.getElementById('productModalOverlay');
        if (overlay) overlay.classList.remove('active');
    }

    if (closeProductModalBtn) {
        closeProductModalBtn.addEventListener('click', closeProductModal);
    }

    // Prevent background scrolling via wheel and touchmove when product modal is active
    if (productModal) {
        productModal.addEventListener('wheel', function(e) {
            if (!productModal.classList.contains('active')) return;
            const dialog = e.target.closest('.product-inquiry-dialog');
            if (dialog) {
                const scrollTop = dialog.scrollTop;
                const scrollHeight = dialog.scrollHeight;
                const height = dialog.clientHeight;
                const delta = e.deltaY;
                const up = delta < 0;

                if (up && scrollTop <= 0) {
                    e.preventDefault();
                } else if (!up && delta + scrollTop >= scrollHeight - height) {
                    e.preventDefault();
                }
                e.stopPropagation();
            } else {
                e.preventDefault();
            }
        }, { passive: false });

        productModal.addEventListener('touchmove', function(e) {
            if (!productModal.classList.contains('active')) return;
            const dialog = e.target.closest('.product-inquiry-dialog');
            if (!dialog) {
                e.preventDefault();
            }
        }, { passive: false });
    }

    // Escape Key Listener for both modals
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            if (productModal && productModal.classList.contains('active')) {
                closeProductModal();
            }
            if (inquiryContainer && inquiryContainer.classList.contains('active')) {
                toggleInquiryForm();
            }
        }
    });

    // Product Card Click Listener (.open-inquiry-btn)
    document.addEventListener('click', function(event) {
        const btn = event.target.closest('.open-inquiry-btn');
        if (btn) {
            event.preventDefault();
            event.stopPropagation();
            if (event.stopImmediatePropagation) event.stopImmediatePropagation();

            const productName = btn.getAttribute('data-product') || "Road Safety Product";
            const productImg = btn.getAttribute('data-product-img') || "";
            const productTitle = btn.getAttribute('data-product-title') || productName;
            const productModel = btn.getAttribute('data-product-model') || "";
            const productUnit = btn.getAttribute('data-product-unit') || "Pcs";
            const productCategory = btn.getAttribute('data-product-category') || "Road Safety";

            openProductModal(productName, productImg, productTitle, productModel, productUnit, productCategory);
        }
    });

    // Product Modal Form Submission Handler
    if (productInquiryForm) {
        productInquiryForm.addEventListener('submit', function(event) {
            event.preventDefault();

            const form = event.target;
            const userName = document.getElementById('prodModalName') ? document.getElementById('prodModalName').value.trim() : "";
            const userPhone = document.getElementById('prodModalPhone') ? document.getElementById('prodModalPhone').value.trim() : "";
            const userEmail = document.getElementById('prodModalEmail') ? document.getElementById('prodModalEmail').value.trim() : "";
            const rawQty = document.getElementById('prodModalQtyInput') ? document.getElementById('prodModalQtyInput').value.trim() : "";
            const userMsg = document.getElementById('prodModalMessage') ? document.getElementById('prodModalMessage').value.trim() : "";

            const productName = document.getElementById('prodModalHiddenName') ? document.getElementById('prodModalHiddenName').value : "Product Inquiry";

            // Quantity / Requirement
            let formattedQty = rawQty;

            const qtyFormattedHidden = document.getElementById('prodModalHiddenQtyFormatted');
            if (qtyFormattedHidden) {
                qtyFormattedHidden.value = formattedQty;
            }

            // Format Customer Code (First 2 letters of Name + Last 4 digits of Phone) to prevent Gmail thread grouping
            let customerCode = "";
            if (userName) {
                const initials = userName.replace(/[^a-zA-Z]/g, "").substring(0, 2).toUpperCase() || "IN";
                const phoneDigits = userPhone.replace(/\D/g, "");
                const last4 = phoneDigits.length >= 4 ? phoneDigits.slice(-4) : (phoneDigits || "0000");
                customerCode = ` - ${initials}-${last4}`;
            }

            const qtySubjectSuffix = formattedQty ? ` [${formattedQty}]` : "";
            const subjectHidden = document.getElementById('prodModalHiddenSubject');
            if (subjectHidden) {
                subjectHidden.value = `Inquiry: ${productName}${qtySubjectSuffix}${customerCode}`;
            }

            // Default message formatting if message text is blank
            const messageField = document.getElementById('prodModalMessage');
            if (messageField && !userMsg) {
                let qtyLine = formattedQty ? `\nEstimated Quantity / Requirement: ${formattedQty}` : "";
                messageField.value = `Hello EcoLuxe Bharat,\n\nI would like to request pricing, technical specifications, and delivery timelines for the following product model:\n\nProduct: ${productName}${qtyLine}\n\nPlease share the official catalog and quotation.`;
            }

            // Set current Page URL
            const urlHidden = document.getElementById('prodModalHiddenUrl');
            if (urlHidden) urlHidden.value = window.location.href;

            const formData = new FormData(form);

            // Show submission overlay
            const overlay = document.getElementById('productModalOverlay');
            const overlayMsg = document.getElementById('productModalOverlayMsg');
            if (overlay && overlayMsg) {
                overlay.classList.add('active');
                overlayMsg.textContent = "⏳ Sending product inquiry...";
            }

            const prodModalStartTime = Date.now();

            const targetUrl = (productInquiryForm && productInquiryForm.action) || window.FORMSUBMIT_URL || "https://formsubmit.co/ajax/temp2temp2222@gmail.com";
            fetch(targetUrl, {
                method: "POST",
                body: formData
            })
            .then(response => {
                const elapsed = Date.now() - prodModalStartTime;
                const remainingSendingDelay = Math.max(0, 3000 - elapsed);
                return new Promise(resolve => setTimeout(() => resolve(response), remainingSendingDelay));
            })
            .then(response => {
                if (response.ok) {
                    if (overlayMsg) overlayMsg.textContent = "✅ Inquiry sent successfully! Our Team will contact you shortly!";
                    form.reset();

                    setTimeout(() => {
                        closeProductModal();
                    }, 3000);
                } else {
                    if (overlayMsg) overlayMsg.textContent = "❌ Failed to send message. Please try again.";
                    setTimeout(() => {
                        if (overlay) overlay.classList.remove('active');
                    }, 3000);
                }
            })
            .catch(error => {
                if (overlayMsg) overlayMsg.textContent = "❌ Network error. Please check your connection.";
                setTimeout(() => {
                    if (overlay) overlay.classList.remove('active');
                }, 3000);
            });
        });
    }

    // Contact Form AJAX Handler (contact.html)
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const name = document.getElementById('contactName') ? document.getElementById('contactName').value.trim() : "";
            const phoneInput = contactForm.querySelector('input[name="Phone Number"]');
            const phone = phoneInput ? phoneInput.value.trim() : "";
            const leadName = name || "New Lead";
            const code = getCustomerCode(name, phone);

            const subjectHidden = document.getElementById('dynamicSubject');
            if (subjectHidden) {
                subjectHidden.value = `${leadName} - Contact Inquiry - ${code}`;
            }

            const pageUrlHidden = document.getElementById('contactPageUrl');
            if (pageUrlHidden) pageUrlHidden.value = window.location.href;

            const statusDiv = document.getElementById('form-status');
            if (statusDiv) {
                statusDiv.style.color = '#50ab3c';
                statusDiv.textContent = '⏳ Sending message...';
            }

            const formData = new FormData(contactForm);

            const contactStartTime = Date.now();

            const targetUrl = (contactForm && contactForm.action) || window.FORMSUBMIT_URL || "https://formsubmit.co/ajax/temp2temp2222@gmail.com";
            fetch(targetUrl, {
                method: "POST",
                body: formData
            })
            .then(response => {
                const elapsed = Date.now() - contactStartTime;
                const remainingSendingDelay = Math.max(0, 3000 - elapsed);
                return new Promise(resolve => setTimeout(() => resolve(response), remainingSendingDelay));
            })
            .then(response => {
                if (response.ok) {
                    if (statusDiv) {
                        statusDiv.style.color = '#28a745';
                        statusDiv.textContent = '✅ Thank you! Your message has been sent successfully. Our team will get back to you shortly.';
                    }
                    contactForm.reset();
                } else {
                    if (statusDiv) {
                        statusDiv.style.color = '#dc3545';
                        statusDiv.textContent = '❌ Failed to send message. Please try again.';
                    }
                }
            })
            .catch(error => {
                if (statusDiv) {
                    statusDiv.style.color = '#dc3545';
                    statusDiv.textContent = '❌ Network error. Please check your connection and try again.';
                }
            });
        });
    }

    // Check query string for direct inquiry link
    const urlParams = new URLSearchParams(window.location.search);
    const inquiryProduct = urlParams.get('inquiry') || urlParams.get('product');
    if (inquiryProduct) {
        setTimeout(() => {
            openProductModal(inquiryProduct, "", inquiryProduct, "", "Pcs");
        }, 800);
    }
});
