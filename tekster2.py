# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import os
import tkinter as tk
from tkinter import messagebox, Scrollbar


def get_title_and_description(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    title = soup.title
    if title:
        title = title.string.strip()
    else:
        title = "Ingen titel fundet"
    description = soup.find("meta", attrs={"name": "description"})
    if description:
        description = description["content"].strip()
    else:
        description = ""
    return title, description


def fetch_data():
    url = url_entry.get()

    if not url:
        messagebox.showerror("Fejl", "Indtast venligst en URL")
        return

    num_results_per_page = 10
    num_pages = 3
    page_urls = []

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    for link in soup.find_all("a"):
        href = link.get("href")
        if href and href.startswith(url) and "#" not in href and "tel:" not in href:
            page_urls.append(href)

    page_urls = list(set(page_urls))
    page_urls = sorted(page_urls, key=lambda x: x.rstrip('/').split("/")[-1])
    page_count = 0

    results_list.delete(0, tk.END)  # Clear listbox before adding new results

    for page_url in page_urls:
        try:
            title, description = get_title_and_description(page_url)
            results_list.insert(tk.END, f"Titel: {title}")
            results_list.insert(tk.END, f"Beskrivelse: {description}")
            results_list.insert(tk.END, f"URL: {page_url}")
            results_list.insert(tk.END, "")  # Add an empty line to separate results
        except Exception as e:
            results_list.insert(tk.END, f"Error: {str(e)}\n\n")
        page_count += 1

    messagebox.showinfo("F\u00E6rdig!", f"Resultaterne er gemt i filen {filename}")



def copy_to_clipboard(event):
    selected_index = results_list.curselection()[0]
    selected_text = results_list.get(selected_index)
    if "Titel:" in selected_text or "Beskrivelse:" in selected_text:
        app.clipboard_clear()
        app.clipboard_append(selected_text.split(": ", 1)[1])
        results_list.itemconfig(selected_index, bg="yellow")
        app.after(1000, reset_highlight, selected_index)  # Reset background color after 1 second



def reset_highlight(index):
    results_list.itemconfig(index, bg="white")

app = tk.Tk()
app.title("URL Skraber")

url_label = tk.Label(app, text="Indtast URL'en for hjemmesiden:")
url_label.pack()

url_entry = tk.Entry(app, width=50)
url_entry.pack()

fetch_button = tk.Button(app, text="Hent data", command=fetch_data)
fetch_button.pack()

scrollbar = Scrollbar(app)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

results_list = tk.Listbox(app, width=100, height=20, yscrollcommand=scrollbar.set)
results_list.pack()

scrollbar.config(command=results_list.yview)

results_list.bind('<ButtonRelease-1>', copy_to_clipboard)

app.mainloop()