#include <QCoreApplication>
#include <QNetworkAccessManager>
#include <QNetworkRequest>
#include <QNetworkReply>
#include <QUrlQuery>
#include <QTimer>
#include <QDebug>
#include <QRegularExpression>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <QList>
#include <QDir>
#include <QFile>
#include <QIODevice>

class MangaParser : public QObject {
    Q_OBJECT
public:
    explicit MangaParser(QObject *parent = nullptr) : QObject(parent) {
        manager = new QNetworkAccessManager(this);
    }

    void fetchMangaData(const QUrl &url) {
        QNetworkRequest request(url);
        QNetworkReply *reply = manager->get(request);

        connect(reply, &QNetworkReply::finished, [this, reply]() {
            if (reply->error() != QNetworkReply::NoError) {
                qDebug() << "Error:" << reply->errorString();
                reply->deleteLater();
                return;
            }

            QString html = reply->readAll();
            reply->deleteLater();
            parseMangaData(html);
        });
    }

signals:
    void parsingFinished(int news_id, const QList<int>& chapter_ids);

private:
    QNetworkAccessManager *manager;

    void parseMangaData(const QString &html) {
        QRegularExpression jsonRegex(R"(window\.__DATA__\s*=\s*(\{.*?\});)");
        QRegularExpressionMatch jsonMatch = jsonRegex.match(html);

        if (!jsonMatch.hasMatch()) {
            qDebug() << "JSON data not found in HTML";
            return;
        }

        QString jsonStr = jsonMatch.captured(1);
        QJsonDocument doc = QJsonDocument::fromJson(jsonStr.toUtf8());

        if (doc.isNull()) {
            qDebug() << "Failed to parse JSON";
            return;
        }

        QJsonObject data = doc.object();
        int news_id = data["news_id"].toInt();
        QJsonArray chapters = data["chapters"].toArray();
        QList<int> chapter_ids;

        for (const auto& chapter : chapters) {
            chapter_ids.append(chapter.toObject()["id"].toInt());
        }

        qDebug() << "Parsed manga data - News ID:" << news_id << "Chapters count:" << chapter_ids.size();
        emit parsingFinished(news_id, chapter_ids);
    }
};

class CurlManager : public QObject {
    Q_OBJECT
public:
    CurlManager(QObject *parent = nullptr) : QObject(parent) {
        manager = new QNetworkAccessManager(this);
    }

    void executeRequests(int news_id, const QList<int>& chapter_ids) {
        this->news_id = news_id;
        this->chapter_ids = chapter_ids;
        current_chapter_index = 0;

        qDebug() << "Starting processing for" << chapter_ids.size() << "chapters";
        if (!chapter_ids.isEmpty()) {
            executeInitialCurl1(); // Выполняем curl1 только один раз в начале
        } else {
            qDebug() << "No chapters found!";
            QCoreApplication::quit();
        }
    }

private:
    QNetworkAccessManager *manager;
    int news_id = 0;
    QList<int> chapter_ids;
    int current_chapter_index = 0;

    void executeInitialCurl1() {
        QUrl url("https://comx.life/mm");
        QNetworkRequest request(url);

        // Оригинальные заголовки curl1 (без изменений)
        request.setRawHeader("accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7");
        request.setRawHeader("accept-language", "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7");
        request.setRawHeader("cache-control", "max-age=0");
        request.setRawHeader("content-type", "application/x-www-form-urlencoded");
        request.setRawHeader("origin", "https://comx.life");
        request.setRawHeader("priority", "u=0, i");
        request.setRawHeader("referer", "https://comx.life/mm");
        request.setRawHeader("sec-ch-ua", "\"Chromium\";v=\"137\", \"Not/A)Brand\";v=\"24\"");
        request.setRawHeader("sec-ch-ua-mobile", "?0");
        request.setRawHeader("sec-ch-ua-platform", "\"Linux\"");
        request.setRawHeader("sec-fetch-dest", "document");
        request.setRawHeader("sec-fetch-mode", "navigate");
        request.setRawHeader("sec-fetch-site", "same-origin");
        request.setRawHeader("sec-fetch-user", "?1");
        request.setRawHeader("upgrade-insecure-requests", "1");
        request.setRawHeader("user-agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36");

        // Оригинальные куки curl1 (без изменений)
        QString cookies = "_ym_uid=1751741300351017237; _ym_d=1751741300; ma_id=3045464071751745424523; __ai_fp_uuid=b60fd0be2d93cfb9%3A1; __upin=/TEepR5EfhsO2YiJbqOp2Q; ma_id_api=ibKRUFJdN2PSwGTV7QFjXScetYiYpbufK2dfogEYpp8DEJFxiGe5T6DnXS08owS22+Gjb4WrtV3UVqUnBBAv1bEtu1ciLo8ogKDhDSIOh5+dy8ugof0cAvl2G87C8x4OAl83YuaaDWmUg1A98Lbo8pgKtGL5+etmuW9Yqy2gC1gZSMcvYOSvjjPY6oEa9mF0hoJ3FugZ1tewa7EOqiSjsV+yZqMP+nBKBEMtkkz62rAgIlwBuBEXNaE3LDhfRaDa02zJ/IIUPr4SYDlxd4h1KGkhdjpAnWzQdFIfyfZfYI/U9n/9IpZFk5oUueXeiWCzOYKH+B6vFR00vl0+/Tz/nQ==; _buzz_aidata=JTdCJTIydWZwJTIyJTNBJTIyJTJGVEVlcFI1RWZoc08yWWlKYnFPcDJRJTIyJTJDJTIyYnJvd3NlclZlcnNpb24lMjIlM0ElMjIxMzcuMCUyMiUyQyUyMnRzQ3JlYXRlZCUyMiUzQTE3NTE3NDU0MzEwMzUlN0Q=; _buzz_mtsa=JTdCJTIydWZwJTIyJTNBJTIyMDg5ZjBhNzI0YWVhODdjMDkzMjBlM2ZjMTY3ODRmMDglMjIlMkMlMjJicm93c2VyVmVyc2lvbiUyMiUzQSUyMjEzNy4wJTIyJTJDJTIydHNDcmVhdGVkJTIyJTNBMTc1MTc0NTQzMjIyMyU3RA==; _ym_isad=2; PHPSESSID=0bca9e9cb7fc697f7dba91da7d143aae; kbSession=17519698081772474; kbCreated=Tue, 08 Jul 2025 10:16:49 GMT; kbRes=true; kbLoaded=true; comi=02a601d64af59e20544dfda7f012621b; kbT=true; kbUserID=942827788327400848";
        request.setRawHeader("cookie", cookies.toUtf8());

        // Оригинальные POST-данные curl1 (без изменений)
        QUrlQuery postData;
        postData.addQueryItem("login_name", "serden");
        postData.addQueryItem("login_password", "vqfce6875c3");
        postData.addQueryItem("login", "submit");

        QNetworkReply *reply = manager->post(request, postData.toString(QUrl::FullyEncoded).toUtf8());
        connect(reply, &QNetworkReply::finished, this, [this, reply]() {
            onInitialCurl1Finished(reply);
        });
    }

    void onInitialCurl1Finished(QNetworkReply *reply) {
        qDebug() << "Initial curl1 finished with status:" << reply->error();
        reply->deleteLater();

        // После выполнения curl1 начинаем обработку глав
        processNextChapter();
    }

    void processNextChapter() {
        if (current_chapter_index >= chapter_ids.size()) {
            qDebug() << "All chapters processed!";
            QCoreApplication::quit();
            return;
        }

        int current_chapter_id = chapter_ids[current_chapter_index];
        qDebug() << "Processing chapter" << current_chapter_index + 1 << "of" << chapter_ids.size() << "| ID:" << current_chapter_id;

        executeCurl2ForChapter(current_chapter_id);
    }

    void executeCurl2ForChapter(int chapter_id) {
        QUrl url("https://comx.life/engine/ajax/controller.php?mod=api&action=chapters/download");
        QNetworkRequest request(url);

        // Оригинальные заголовки curl2 (без изменений)
        request.setRawHeader("accept", "application/json, text/javascript, */*; q=0.01");
        request.setRawHeader("accept-language", "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7");
        request.setRawHeader("content-type", "application/x-www-form-urlencoded; charset=UTF-8");
        request.setRawHeader("origin", "https://comx.life");
        request.setRawHeader("priority", "u=1, i");
        request.setRawHeader("referer", "https://comx.life/10889-kakkou-no-iinazuke-svedennye-kukushkoj.html");
        request.setRawHeader("sec-ch-ua", "\"Chromium\";v=\"137\", \"Not/A)Brand\";v=\"24\"");
        request.setRawHeader("sec-ch-ua-mobile", "?0");
        request.setRawHeader("sec-ch-ua-platform", "\"Linux\"");
        request.setRawHeader("sec-fetch-dest", "empty");
        request.setRawHeader("sec-fetch-mode", "cors");
        request.setRawHeader("sec-fetch-site", "same-origin");
        request.setRawHeader("user-agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36");
        request.setRawHeader("x-requested-with", "XMLHttpRequest");

        // Оригинальные куки curl2 (без изменений)
        QString cookies = "_ym_uid=1751741300351017237; _ym_d=1751741300; ma_id=3045464071751745424523; __ai_fp_uuid=b60fd0be2d93cfb9%3A1; __upin=/TEepR5EfhsO2YiJbqOp2Q; ma_id_api=ibKRUFJdN2PSwGTV7QFjXScetYiYpbufK2dfogEYpp8DEJFxiGe5T6DnXS08owS22+Gjb4WrtV3UVqUnBBAv1bEtu1ciLo8ogKDhDSIOh5+dy8ugof0cAvl2G87C8x4OAl83YuaaDWmUg1A98Lbo8pgKtGL5+etmuW9Yqy2gC1gZSMcvYOSvjjPY6oEa9mF0hoJ3FugZ1tewa7EOqiSjsV+yZqMP+nBKBEMtkkz62rAgIlwBuBEXNaE3LDhfRaDa02zJ/IIUPr4SYDlxd4h1KGkhdjpAnWzQdFIfyfZfYI/U9n/9IpZFk5oUueXeiWCzOYKH+B6vFR00vl0+/Tz/nQ==; _buzz_aidata=JTdCJTIydWZwJTIyJTNBJTIyJTJGVEVlcFI1RWZoc08yWWlKYnFPcDJRJTIyJTJDJTIyYnJvd3NlclZlcnNpb24lMjIlM0ElMjIxMzcuMCUyMiUyQyUyMnRzQ3JlYXRlZCUyMiUzQTE3NTE3NDU0MzEwMzUlN0Q=; _buzz_mtsa=JTdCJTIydWZwJTIyJTNBJTIyMDg5ZjBhNzI0YWVhODdjMDkzMjBlM2ZjMTY3ODRmMDglMjIlMkCJTIyYnJvd3NlclZlcnNpb24lMjIlM0ElMjIxMzcuMCUyMiUyQyUyMnRzQ3JlYXRlZCUyMiUzQTE3NTE3NDU0MzIyMjMlN0Q=; _ym_isad=2; kbSession=17519698081772474; kbRes=true; kbLoaded=true; comi=02a601d64af59e20544dfda7f012621b; kbT=true; kbUserID=942827788327400848; PHPSESSID=53187921b7cbda255d8dbb825fa1bf15; dle_user_id=557759; dle_password=8eaab7f4befacd64527997ae5c5449a1; dle_newpm=0; viewed_ids=10889,9919,11944,19600,13554,9451,19597,17864,6888,17433; kbCreated=Tue, 08 Jul 2025 10:18:40 GMT";
        request.setRawHeader("cookie", cookies.toUtf8());

        // Динамические POST-данные для текущей главы
        QUrlQuery postData;
        postData.addQueryItem("chapter_id", QString::number(chapter_id));
        postData.addQueryItem("news_id", QString::number(news_id));

        QNetworkReply *reply = manager->post(request, postData.toString(QUrl::FullyEncoded).toUtf8());
        connect(reply, &QNetworkReply::finished, this, [this, reply]() {
            onCurl2Finished(reply);
        });
    }

    void onCurl2Finished(QNetworkReply *reply) {
        if (reply->error() != QNetworkReply::NoError) {
            qDebug() << "Curl2 error:" << reply->errorString();
            reply->deleteLater();
            processNextChapter();
            return;
        }

        QString response = reply->readAll();
        reply->deleteLater();

        QJsonDocument doc = QJsonDocument::fromJson(response.toUtf8());
        if (!doc.isNull() && doc.object().value("success").toBool()) {
            QString downloadUrl = doc.object().value("data").toString();
            downloadUrl = downloadUrl.replace("\\/", "/").replace("\"", ""); // Удаляем лишние кавычки если есть
            qDebug() << "Original download URL:" << downloadUrl;

            // Загружаем CBR файл
            downloadCbrFile(downloadUrl);
        } else {
            qDebug() << "Invalid JSON or unsuccessful response";
            processNextChapter();
        }
    }

    void downloadCbrFile(const QString &url) {
        QString fullUrl = url;
        // Добавляем https: если URL начинается с //
        if (fullUrl.startsWith("//")) {
            fullUrl = "https:" + fullUrl;
        }
        // Или добавляем https:// если URL вообще без протокола
        else if (!fullUrl.startsWith("http")) {
            fullUrl = "https://" + fullUrl;
        }

        qDebug() << "Final download URL:" << fullUrl;

        QNetworkRequest request;
        request.setUrl(QUrl(fullUrl));

        request.setRawHeader("User-Agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36");
        request.setRawHeader("Referer", "https://comx.life/");

        QNetworkReply *reply = manager->get(request);
        connect(reply, &QNetworkReply::finished, this, [this, reply]() {
            onCbrDownloadFinished(reply);
        });

        connect(reply, &QNetworkReply::downloadProgress, [this](qint64 bytesReceived, qint64 bytesTotal) {
            qDebug() << "Download progress:" << bytesReceived << "/" << bytesTotal << "bytes";
        });
    }



    void onCbrDownloadFinished(QNetworkReply *reply) {
        if (reply->error() == QNetworkReply::NoError) {
            QDir dir;
            if (!dir.exists("downloads")) {
                dir.mkdir("downloads");
            }

            // Генерируем имя файла в формате Chapter1.cbr, Chapter2.cbr и т.д.
            QString filename = QString("downloads/Chapter%1.cbr")
                              .arg(current_chapter_index + 1); // +1 чтобы начинать с 1

            QFile file(filename);
            if (file.open(QIODevice::WriteOnly)) {
                file.write(reply->readAll());
                file.close();
                qDebug() << "File saved:" << filename;
            } else {
                qDebug() << "Failed to save file:" << filename;
            }
        } else {
            qDebug() << "Download failed:" << reply->errorString();
        }

        reply->deleteLater();

        // Увеличиваем индекс главы
        current_chapter_index++;

        // Добавляем задержку и переходим к следующей главе
        QTimer::singleShot(1000, this, &CurlManager::processNextChapter);
    }


};

int main(int argc, char *argv[]) {
    QCoreApplication a(argc, argv);

    MangaParser parser;
    CurlManager manager;

    QObject::connect(&parser, &MangaParser::parsingFinished,
                     &manager, &CurlManager::executeRequests);

    QUrl mangaUrl("https://comx.life/10889-kakkou-no-iinazuke-svedennye-kukushkoj.html#chapters");
    parser.fetchMangaData(mangaUrl);

    return a.exec();
}

#include "main.moc"
