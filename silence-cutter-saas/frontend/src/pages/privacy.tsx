import { NextPage } from "next";
import Layout from "@/components/layout/Layout";

const PrivacyPolicyPage: NextPage = () => {
  return (
    <Layout title="Privacy Policy - Silence Cutter">
      <div className="bg-gray-50 min-h-screen py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white p-8 rounded-lg shadow-sm">
            <h1 className="text-3xl font-bold text-gray-900 mb-6">
              Privacy Policy
            </h1>
            <p className="text-gray-600 mb-4">
              Last updated: {new Date().toLocaleDateString()}
            </p>

            <div className="prose max-w-none">
              <h2>1. Introduction</h2>
              <p>
                Welcome to Silence Cutter ("we," "our," or "us"). We are
                committed to protecting your privacy and handling your data in
                an open and transparent manner. This Privacy Policy explains how
                we collect, use, disclose, and safeguard your information when
                you use our video processing service.
              </p>

              <h2>2. Information We Collect</h2>
              <h3>2.1 Personal Information</h3>
              <p>
                We may collect personal information that you provide directly to
                us, including:
              </p>
              <ul>
                <li>
                  Name and contact information (email address, phone number)
                </li>
                <li>Account credentials (username, password)</li>
                <li>
                  Billing information (credit card details, billing address)
                </li>
                <li>User profile information</li>
              </ul>

              <h3>2.2 Video Content</h3>
              <p>
                When you upload videos to our service, we collect and process
                the video files and associated metadata. We do not claim
                ownership of your content. You retain all rights to your videos.
              </p>

              <h3>2.3 Usage Information</h3>
              <p>
                We automatically collect certain information about your
                interactions with our service, including:
              </p>
              <ul>
                <li>
                  Log data (IP address, browser type, pages visited, time spent)
                </li>
                <li>Device information (device type, operating system)</li>
                <li>Usage patterns and preferences</li>
              </ul>

              <h2>3. How We Use Your Information</h2>
              <p>
                We use the information we collect for various purposes,
                including:
              </p>
              <ul>
                <li>Providing and maintaining our service</li>
                <li>Processing and fulfilling your requests</li>
                <li>Processing payments and managing your account</li>
                <li>
                  Sending service announcements and responding to your inquiries
                </li>
                <li>Improving and personalizing our service</li>
                <li>Ensuring the security and integrity of our service</li>
                <li>Complying with legal obligations</li>
              </ul>

              <h2>4. Data Storage and Security</h2>
              <p>
                We implement appropriate technical and organizational measures
                to protect your personal information against unauthorized or
                unlawful processing, accidental loss, destruction, or damage.
                Your video content is stored in secure cloud storage and
                processed on secure servers.
              </p>
              <p>
                While we strive to use commercially acceptable means to protect
                your personal information, we cannot guarantee its absolute
                security.
              </p>

              <h2>5. Data Retention</h2>
              <p>
                We retain your personal information for as long as necessary to
                provide you with our services and for legitimate and essential
                business purposes, such as maintaining the performance of our
                service, making data-driven business decisions, complying with
                our legal obligations, and resolving disputes.
              </p>
              <p>
                You can delete your account or request deletion of your video
                content at any time through your account settings.
              </p>

              <h2>6. Sharing Your Information</h2>
              <p>
                We may share your information with third parties in the
                following circumstances:
              </p>
              <ul>
                <li>
                  Service providers who assist us in operating our service
                </li>
                <li>Payment processors for processing transactions</li>
                <li>
                  Professional advisors, such as lawyers, auditors, and insurers
                </li>
                <li>
                  Regulatory authorities, government agencies, and law
                  enforcement
                </li>
                <li>Potential buyers in the event of a business transaction</li>
              </ul>

              <h2>7. Your Rights</h2>
              <p>
                Depending on your location, you may have certain rights
                regarding your personal information:
              </p>
              <ul>
                <li>Access to your personal information</li>
                <li>Correction of inaccurate or incomplete information</li>
                <li>Deletion of your personal information</li>
                <li>Restriction or objection to processing</li>
                <li>Data portability</li>
                <li>Withdrawal of consent</li>
              </ul>

              <h2>8. Children's Privacy</h2>
              <p>
                Our service is not intended for individuals under the age of 13.
                We do not knowingly collect personal information from children
                under 13. If you are a parent or guardian and believe that your
                child has provided us with personal information, please contact
                us.
              </p>

              <h2>9. International Data Transfers</h2>
              <p>
                Your information may be transferred to and processed in
                countries other than the country in which you are a resident.
                These countries may have data protection laws that are different
                from those of your country. We implement appropriate safeguards
                to protect your information when it is transferred.
              </p>

              <h2>10. Changes to this Privacy Policy</h2>
              <p>
                We may update this Privacy Policy from time to time to reflect
                changes in our practices or for other operational, legal, or
                regulatory reasons. The updated policy will be posted on this
                page with a revised effective date.
              </p>

              <h2>11. Contact Us</h2>
              <p>
                If you have any questions or concerns about this Privacy Policy
                or our privacy practices, please contact us at:
              </p>
              <p>
                <strong>Email:</strong> privacy@silencecutter.com
                <br />
                <strong>Address:</strong> 123 Privacy Street, Tech City, TC
                12345
              </p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default PrivacyPolicyPage;
