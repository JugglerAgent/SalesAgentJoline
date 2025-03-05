from services.menu_html_generator import MenuHtmlGenerator

def main():
    """
    Test the menu HTML generator functionality.
    This will generate HTML menu files from the restaurant data.
    """
    print("=== Menu HTML Generator Test ===")
    print("Generating HTML menu files from restaurant_data.json...")
    
    generator = MenuHtmlGenerator()
    result = generator.generate_all_menus()
    
    if result:
        print("Successfully generated the following HTML menu files:")
        print("- attachments/a_la_carte_menu.html")
        print("- attachments/breakfast_menu.html")
        print("- attachments/kiddies_menu.html")
        print("- attachments/drinks_menu.html")
        print("- attachments/wine_list.html")
    else:
        print("Failed to generate HTML menu files.")

if __name__ == "__main__":
    main()