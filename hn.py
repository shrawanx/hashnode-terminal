import requests


def create_query_for_post_list(username, page):
    return """{
      user(username: "%s") {
        username,
        name,
        tagline,
        publicationDomain,
        publication{
            title,
            meta,
            posts(page:%d){
                slug,
                title,
                brief
            }
        }
      }
    }""" % (username, page)


def create_query_for_post_detail(slug, hostname):
    return """{
        post(slug:"%s",hostname:"%s"){
            dateAdded,
            content
        }
    }""" % (slug, hostname)


def request_hashnode_dot_com(query):
    return requests.post("https://api.hashnode.com/",
                         json={'query': query})


def create_plain_text_from_html(html):
    from html.parser import HTMLParser

    class _CustomHTMLParser(HTMLParser):
        normal_text = ""

        def handle_data(self, data):
            self.normal_text += data

    f = _CustomHTMLParser()
    f.feed(html)
    return f.normal_text


def show_post_detail(article, publication_domain):
    q = create_query_for_post_detail(
        article['slug'], publication_domain
    )
    post_detail_reponse = request_hashnode_dot_com(q)
    if post_detail_reponse.status_code == 200:
        content = post_detail_reponse.json()['data']['post']['content']
        date_added = post_detail_reponse.json()['data']['post']['dateAdded']
        print(article['title'].upper())
        print("Added on:", date_added)
        print(create_plain_text_from_html(content))
    else:
        print("Error")
        exit(1)


def main():
    import sys
    username = sys.argv[1] if len(sys.argv) == 2 else "pydj"
    current_page = 0
    articles = {}

    while True:
        query = create_query_for_post_list(username, current_page)
        response = request_hashnode_dot_com(query)
        if response.status_code == 200:
            if not response.json()['data']["user"]["username"]:
                print("Invalid User")
                exit(1)
            re_data = response.json()['data']["user"]
            print("Welcome to:", re_data['publication']['title'])
            print("----List of Articles----")
            if not re_data['publication']['posts']:
                print("***No Articles Available, try changing page number***")
            else:
                for index, article in enumerate(re_data['publication']['posts'], 1):
                    articles[index] = article
                    print(f"[{index}]", article['title'])

            print("Current Page:", current_page + 1)
            print("-----------------")
            print(f"Type: n for next page\n"
                  f"      p for previous page\n"
                  f"      1-{len(articles)} for article detail")
            print("-----------------")

            user_input = input("Enter your input: ")

            valid_inputs = ["n", "p"] + [str(i) for i in articles.keys()]
            if user_input not in valid_inputs:
                print("Invalid choice")
                exit(1)
            if user_input == "n":
                current_page += 1
                continue
            if user_input == "p":
                if current_page == 0:
                    print("Cannot go to previous page")
                    exit(1)
                else:
                    current_page -= 1
                    continue

            show_post_detail(articles[int(user_input)], re_data['publicationDomain'])
            break

        else:
            print("error")
            exit(1)


if __name__ == '__main__':
    main()
