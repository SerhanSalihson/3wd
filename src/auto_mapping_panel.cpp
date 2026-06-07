#include "omni/auto_mapping_panel.hpp"

#include <QLabel>
#include <QPushButton>
#include <QVBoxLayout>

#include "ament_index_cpp/get_package_prefix.hpp"
#include "pluginlib/class_list_macros.hpp"

namespace omni
{

AutoMappingPanel::AutoMappingPanel(QWidget * parent)
: rviz_common::Panel(parent), mapper_process_(new QProcess(this)), stop_requested_(false)
{
  auto * title = new QLabel("Automatic Mapping: Master of Frontiers", this);
  QFont title_font = title->font();
  title_font.setBold(true);
  title_font.setPointSize(title_font.pointSize() + 2);
  title->setFont(title_font);

  auto * description = new QLabel(
    "Explore map frontiers with Nav2 and save the completed map to "
    "~/omni/maps/auto_map.yaml.", this);
  description->setWordWrap(true);

  start_button_ = new QPushButton("START AUTO MAPPING (Seek and Destroy)", this);
  start_button_->setMinimumHeight(42);
  start_button_->setStyleSheet(
    "QPushButton { background-color: #2e7d32; color: white; font-weight: bold; }"
    "QPushButton:disabled { background-color: #555; color: #aaa; }");

  stop_button_ = new QPushButton("STOP MAPPING (Hit the Lights)", this);
  stop_button_->setMinimumHeight(34);
  stop_button_->setEnabled(false);
  stop_button_->setStyleSheet(
    "QPushButton { background-color: #a52a2a; color: white; font-weight: bold; }"
    "QPushButton:disabled { background-color: #555; color: #aaa; }");

  status_label_ = new QLabel(this);
  status_label_->setAlignment(Qt::AlignCenter);
  status_label_->setMinimumHeight(28);
  setStatus("READY", "#90caf9");

  auto * layout = new QVBoxLayout;
  layout->addWidget(title);
  layout->addWidget(description);
  layout->addSpacing(8);
  layout->addWidget(start_button_);
  layout->addWidget(stop_button_);
  layout->addSpacing(6);
  layout->addWidget(status_label_);
  layout->addStretch();
  setLayout(layout);

  connect(start_button_, &QPushButton::clicked, this, &AutoMappingPanel::startMapping);
  connect(stop_button_, &QPushButton::clicked, this, &AutoMappingPanel::stopMapping);
  connect(mapper_process_, &QProcess::started, this, &AutoMappingPanel::processStarted);
  connect(
    mapper_process_,
    qOverload<int, QProcess::ExitStatus>(&QProcess::finished),
    this, &AutoMappingPanel::processFinished);
  connect(
    mapper_process_, &QProcess::errorOccurred,
    this, &AutoMappingPanel::processError);
}

AutoMappingPanel::~AutoMappingPanel()
{
  if (mapper_process_->state() != QProcess::NotRunning) {
    mapper_process_->terminate();
    if (!mapper_process_->waitForFinished(2000)) {
      mapper_process_->kill();
      mapper_process_->waitForFinished(1000);
    }
  }
}

void AutoMappingPanel::startMapping()
{
  if (mapper_process_->state() != QProcess::NotRunning) {
    return;
  }

  stop_requested_ = false;
  setStatus("STARTING...", "#ffcc80");
  start_button_->setEnabled(false);
  try {
    const auto package_prefix = ament_index_cpp::get_package_prefix("omni");
    mapper_process_->setProgram(
      QString::fromStdString(package_prefix + "/lib/omni/auto_mapper.py"));
    mapper_process_->setArguments({});
    mapper_process_->setProcessChannelMode(QProcess::ForwardedChannels);
    mapper_process_->start();
  } catch (const std::exception & error) {
    setRunning(false);
    setStatus(QString("PACKAGE ERROR: %1").arg(error.what()), "#ef9a9a");
  }
}

void AutoMappingPanel::stopMapping()
{
  if (mapper_process_->state() == QProcess::NotRunning) {
    return;
  }

  stop_requested_ = true;
  setStatus("STOPPING...", "#ffcc80");
  stop_button_->setEnabled(false);
  mapper_process_->terminate();
  if (!mapper_process_->waitForFinished(2000)) {
    mapper_process_->kill();
  }
}

void AutoMappingPanel::processStarted()
{
  setRunning(true);
  setStatus("AUTO MAPPING ACTIVE", "#81c784");
}

void AutoMappingPanel::processFinished(int exit_code, QProcess::ExitStatus exit_status)
{
  setRunning(false);
  if (stop_requested_) {
    setStatus("STOPPED", "#90caf9");
  } else if (exit_status == QProcess::NormalExit && exit_code == 0) {
    setStatus("MAPPING FINISHED (Nothing Else Matters)", "#81c784");
  } else {
    setStatus(QString("MAPPER EXITED (%1)").arg(exit_code), "#ef9a9a");
  }
  stop_requested_ = false;
}

void AutoMappingPanel::processError(QProcess::ProcessError error)
{
  setRunning(false);
  setStatus(QString("START ERROR (%1)").arg(static_cast<int>(error)), "#ef9a9a");
}

void AutoMappingPanel::setRunning(bool running)
{
  start_button_->setEnabled(!running);
  stop_button_->setEnabled(running);
}

void AutoMappingPanel::setStatus(const QString & text, const QString & color)
{
  status_label_->setText(text);
  status_label_->setStyleSheet(
    QString("QLabel { color: %1; font-weight: bold; }").arg(color));
}

}  // namespace omni

PLUGINLIB_EXPORT_CLASS(omni::AutoMappingPanel, rviz_common::Panel)
