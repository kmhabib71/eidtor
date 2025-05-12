import Link from "next/link";

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gray-50 border-t border-gray-200">
      <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="mb-4 md:mb-0">
            <p className="text-gray-600 text-sm">
              &copy; {currentYear} Silence Cutter. All rights reserved.
            </p>
          </div>
          <div className="flex space-x-6">
            <Link
              href="/help"
              className="text-gray-600 hover:text-gray-900 text-sm"
            >
              Help
            </Link>
            <Link
              href="/privacy"
              className="text-gray-600 hover:text-gray-900 text-sm"
            >
              Privacy Policy
            </Link>
            <Link
              href="/terms"
              className="text-gray-600 hover:text-gray-900 text-sm"
            >
              Terms of Service
            </Link>
            <Link
              href="/contact"
              className="text-gray-600 hover:text-gray-900 text-sm"
            >
              Contact Us
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
