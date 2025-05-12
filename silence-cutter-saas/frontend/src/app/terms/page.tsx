export default function TermsOfServicePage() {
  return (
    <div className="bg-gray-50 min-h-screen py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white p-8 rounded-lg shadow-sm">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">
            Terms of Service
          </h1>
          <p className="text-gray-600 mb-4">
            Last updated: {new Date().toLocaleDateString()}
          </p>

          <div className="prose max-w-none">
            <h2>1. Introduction</h2>
            <p>
              Welcome to Silence Cutter. These Terms of Service ("Terms") govern
              your use of our website, application, and video processing
              services. By accessing or using our Service, you agree to be bound
              by these Terms. If you disagree with any part of the Terms, you
              may not access the Service.
            </p>

            <h2>2. Definitions</h2>
            <p>For the purposes of these Terms:</p>
            <ul>
              <li>
                <strong>Service</strong> refers to the Silence Cutter website,
                application, and video processing services.
              </li>
              <li>
                <strong>User</strong> refers to the individual accessing or
                using the Service, or the company, or other legal entity on
                behalf of which such individual is accessing or using the
                Service.
              </li>
              <li>
                <strong>Content</strong> refers to any data or information,
                including videos, that you upload, process, or otherwise submit
                to the Service.
              </li>
              <li>
                <strong>Account</strong> refers to a unique account created for
                you to access our Service.
              </li>
            </ul>

            <h2>3. Account Registration</h2>
            <p>
              To use certain features of the Service, you must register for an
              account. When you register, you must provide accurate and complete
              information. You are responsible for maintaining the security of
              your account and password, and you accept responsibility for all
              activities that occur under your account.
            </p>

            <h2>4. Subscription and Payments</h2>
            <h3>4.1 Subscription Plans</h3>
            <p>
              Silence Cutter offers various subscription plans with different
              features and limitations. The features and limitations of each
              plan are described on our website.
            </p>

            <h3>4.2 Payment Terms</h3>
            <p>
              Subscriptions are billed in advance on a monthly or annual basis.
              Payment will be charged to your designated payment method at the
              confirmation of your subscription. Subscription fees are
              non-refundable.
            </p>

            <h3>4.3 Subscription Cancellation</h3>
            <p>
              You can cancel your subscription at any time through your account
              settings. Upon cancellation, your subscription will remain active
              until the end of your current billing period.
            </p>

            <h2>5. User Content</h2>
            <h3>5.1 Ownership</h3>
            <p>
              You retain all rights to your Content. By uploading Content to the
              Service, you grant us a non-exclusive, worldwide, royalty-free
              license to use, process, and store your Content for the purpose of
              providing the Service to you.
            </p>

            <h3>5.2 Content Restrictions</h3>
            <p>You agree not to upload, process, or share Content that:</p>
            <ul>
              <li>Violates any applicable laws or regulations</li>
              <li>Infringes on the intellectual property rights of others</li>
              <li>Contains harmful, offensive, or inappropriate material</li>
              <li>Contains malware, viruses, or any harmful code</li>
            </ul>

            <h2>6. Acceptable Use</h2>
            <p>You agree not to use the Service to:</p>
            <ul>
              <li>Violate any laws or regulations</li>
              <li>Impersonate any person or entity</li>
              <li>
                Engage in any activity that interferes with or disrupts the
                Service
              </li>
              <li>
                Attempt to gain unauthorized access to the Service or related
                systems
              </li>
              <li>Use the Service for any illegal or unauthorized purpose</li>
            </ul>

            <h2>7. Intellectual Property</h2>
            <p>
              The Service and its original content (excluding Content provided
              by users), features, and functionality are and will remain the
              exclusive property of Silence Cutter and its licensors. The
              Service is protected by copyright, trademark, and other laws of
              both the United States and foreign countries.
            </p>

            <h2>8. Limitation of Liability</h2>
            <p>
              In no event shall Silence Cutter, its directors, employees,
              partners, agents, suppliers, or affiliates, be liable for any
              indirect, incidental, special, consequential, or punitive damages,
              including without limitation, loss of profits, data, use,
              goodwill, or other intangible losses, resulting from your access
              to or use of or inability to access or use the Service.
            </p>

            <h2>9. Disclaimer</h2>
            <p>
              The Service is provided on an "AS IS" and "AS AVAILABLE" basis.
              Silence Cutter does not warrant that the Service will be
              uninterrupted, secure, or error-free. We do not warrant that the
              results that may be obtained from the use of the Service will be
              accurate or reliable.
            </p>

            <h2>10. Termination</h2>
            <p>
              We may terminate or suspend your account and bar access to the
              Service immediately, without prior notice or liability, under our
              sole discretion, for any reason whatsoever, including without
              limitation if you breach the Terms.
            </p>

            <h2>11. Changes to Terms</h2>
            <p>
              We reserve the right to modify or replace these Terms at any time.
              We will provide notice of changes to the Terms by posting the
              updated Terms on this page with a new effective date. Your
              continued use of the Service after any such changes constitutes
              your acceptance of the new Terms.
            </p>

            <h2>12. Governing Law</h2>
            <p>
              These Terms shall be governed and construed in accordance with the
              laws of the United States, without regard to its conflict of law
              provisions.
            </p>

            <h2>13. Contact Us</h2>
            <p>
              If you have any questions about these Terms, please contact us at:
            </p>
            <p>
              <strong>Email:</strong> legal@silencecutter.com
              <br />
              <strong>Address:</strong> 123 Legal Avenue, Tech City, TC 12345
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
