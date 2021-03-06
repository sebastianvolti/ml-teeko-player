import matplotlib.pyplot as plt


def plot_means(x_data, y_data, totals_mean):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    fig.subplots_adjust(top=0.85)
    ax.set_title("Promedio de ganadas: {}%".format(totals_mean))
    ax.set_ylim([0, 120])
    ax.plot([0, len(x_data)], [100, 100], 'k')
    ax.plot(x_data, y_data, 'r')
    plt.show()


def plot_acc_wins(x_data, y_data, y_data_2):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    fig.subplots_adjust(top=0.85)
    ax.set_title("Comparación de partidas ganadas")
    ax.plot(x_data, y_data, 'r')
    ax.plot(x_data, y_data_2, 'b')
    ax.legend(['Jugador 1', 'Oponente'])
    plt.show()


def plot_pie_wins_losses(sizes, labels, title):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    fig.subplots_adjust(top=0.85)
    ax.set_title(title)
    ax.pie(sizes, labels=labels, autopct='%1.1f%%')
    plt.show()

